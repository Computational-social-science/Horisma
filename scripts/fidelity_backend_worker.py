"""One offline parser backend, fixed inputs, raw retained output; no labels supplied."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def make_adapter(root, backend):
    if backend == 'docling':
        from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import PdfPipelineOptions, RapidOcrOptions
        from docling.datamodel.accelerator_options import AcceleratorOptions, AcceleratorDevice
        models = Path('C:/Users/Administrator/AppData/Roaming/Python/Python314/site-packages/rapidocr/models')
        options = PdfPipelineOptions(do_ocr=True, do_table_structure=False, enable_remote_services=False, document_timeout=90)
        options.layout_options.model_spec=options.layout_options.model_spec.model_copy(update={
            'revision':'8f39ad3c0b4c58e9c2d2c84a38465abf757272d8'})
        options.ocr_options = RapidOcrOptions(
            backend='onnxruntime', lang=['en'], force_full_page_ocr=True,
            det_model_path=str(models / 'PP-OCRv6_det_small.onnx'),
            rec_model_path=str(models / 'PP-OCRv6_rec_small.onnx'),
            cls_model_path=str(models / 'ch_ppocr_mobile_v2.0_cls_mobile.onnx'))
        options.accelerator_options = AcceleratorOptions(device=AcceleratorDevice.CUDA, num_threads=4)
        converter = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options),
                                                     InputFormat.IMAGE: ImageFormatOption(pipeline_options=options)})

        def parse(path, kind):
            result = converter.convert(path)
            raw = result.document.export_to_dict()
            return raw, {'producer_status': result.status.value, 'furniture_filtered': False,
                                 'mode': 'DOCLING_IMAGE_FORCE_OCR', 'device_requested': 'cuda',
                                 'layout_revision':options.layout_options.model_spec.revision}
        return parse
    if backend == 'paddleocr':
        from paddleocr import PaddleOCR, PPStructureV3
        models = root / '.rebuild/tools/paddleocr/models'
        common = {'text_detection_model_name': 'PP-OCRv5_mobile_det',
                  'text_detection_model_dir': str(models / 'PP-OCRv5_mobile_det'),
                  'text_recognition_model_name': 'en_PP-OCRv5_mobile_rec',
                  'text_recognition_model_dir': str(models / 'en_PP-OCRv5_mobile_rec'),
                  'use_doc_orientation_classify': False, 'use_doc_unwarping': False,
                  'use_textline_orientation': False, 'device': 'cpu', 'enable_mkldnn': False, 'cpu_threads': 4}
        ocr = PaddleOCR(**common)
        layout = PPStructureV3(**common, layout_detection_model_name='PP-DocLayout_plus-L',
                              layout_detection_model_dir=str(root / '.rebuild/tools/paddleocr/layout-models/PP-DocLayout_plus-L'),
                              use_table_recognition=False, use_formula_recognition=False,
                              use_seal_recognition=False, use_chart_recognition=False,
                              use_region_detection=False, format_block_content=False, markdown_ignore_labels=[])

        def parse(path, kind):
            engine = layout if kind == 'page' else ocr
            result = list(engine.predict(str(path)))
            if len(result) != 1:
                raise ValueError('ONE_IMAGE_RESULT_REQUIRED')
            raw = result[0].json
            # Serialize through the producer JSON representation before normalization.
            if isinstance(raw, str):
                raw = json.loads(raw)
            return raw, {'mode': 'PPSTRUCTURE_V3' if kind == 'page' else 'PADDLE_REGIONAL_OCR',
                                 'ignored_markdown_labels': [], 'device_requested': 'cpu'}
        return parse
    if backend == 'mineru':
        from mineru.config import get_config
        from mineru.parser import MinerUParser
        config = get_config()
        if (config.model.source != 'local' or config.model.vlm.server_url
                or config.llm_aided.features.title_leveling or config.llm_aided.features.cross_page_table_cell_merge):
            raise ValueError('MINERU_OFFLINE_BASIC_POLICY_REQUIRED')
        engine = MinerUParser(tier='basic', parse_mode='ocr', image_analysis=True)

        def parse(path, kind):
            result = engine.parse(path)
            raw = result.middle_json.to_dict(exclude_block_fields={'image_base64'})
            return raw, {'mode': 'MINERU_BASIC_ONNX', 'vlm_used': False,
                                 'device_requested': 'cpu', 'embedded_images_omitted_input_retained': True}
        return parse
    raise ValueError('UNSUPPORTED_BACKEND')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--request-sha256', required=True)
    args = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    raw = args.request.read_bytes()
    if sha(raw) != args.request_sha256:
        raise ValueError('REQUEST_CHANGED')
    request = json.loads(raw); output = args.request.parent
    if not output.resolve().is_relative_to(root / 'outputs/fidelity-campaigns'):
        raise ValueError('EXTERNAL_CAMPAIGN')
    if sha(Path(__file__).read_bytes()) != request['worker_sha256']:
        raise ValueError('WORKER_CHANGED')
    if sha((root/'src/horisma_p0/fidelity_blocks.py').read_bytes())!=request['normalizer_sha256']:
        raise ValueError('NORMALIZER_CHANGED')
    model_raw = (root / request['model_manifest_path']).read_bytes()
    if sha(model_raw) != request['model_manifest_sha256']:
        raise ValueError('MODEL_MANIFEST_CHANGED')
    for name, info in json.loads(model_raw)['backend_files'][request['backend']].items():
        path = Path(name) if Path(name).is_absolute() else root / name
        if sha(path.read_bytes()) != info['sha256']:
            raise ValueError('MODEL_CHANGED:' + path.name)
    os.environ['HF_HUB_OFFLINE'] = '1'; os.environ['TRANSFORMERS_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'; os.environ['MINERU_TELEMETRY_DISABLED'] = '1'
    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
    os.environ['PADDLE_PDX_CACHE_HOME'] = str(root / '.rebuild/tools/paddleocr/cache')

    def block_network(event, _args):
        if event == 'socket.connect':
            raise OSError('OFFLINE_CAMPAIGN_NETWORK_BLOCKED')
    sys.addaudithook(block_network)

    def progress(phase, job=None):
        data = json.dumps({'owner_token': request['owner_token'], 'phase': phase, 'job_id': job})
        temporary = output / 'progress.pending'
        temporary.write_text(data, encoding='utf-8'); os.replace(temporary, output / 'progress.json')
    progress('INITIALIZING')
    from importlib.metadata import version
    if version(request['backend']) != request['backend_version']:
        raise ValueError('BACKEND_VERSION_CHANGED')
    sys.path.insert(0, str(root / 'src'))
    global normalize_blocks
    from horisma_p0.fidelity_blocks import normalize_blocks
    engine = make_adapter(root, request['backend'])
    for job in request['jobs']:
        progress('RUNNING', job['job_id']); started = time.monotonic()
        row = {'job_id': job['job_id'], 'backend': request['backend'], 'input_sha256': job['png_sha256'],
               'scientific_acceptance': False, 'fidelity_qualified': False}
        try:
            path = root / job['png_path']
            if not path.resolve().is_relative_to(root / 'outputs/fidelity-suites') or sha(path.read_bytes()) != job['png_sha256']:
                raise ValueError('FROZEN_IMAGE_CHANGED')
            raw_result, mode = engine(path, job['kind'])

            def encoder(value):
                if hasattr(value, 'tolist'):
                    return value.tolist()
                raise TypeError('UNSUPPORTED_RESULT_TYPE:' + type(value).__name__)
            raw_bytes = json.dumps(raw_result, ensure_ascii=False, indent=2, default=encoder).encode()
            (output / (job['job_id'] + '.raw.json')).write_bytes(raw_bytes)
            row['raw_output_sha256']=sha(raw_bytes)
            blocks=normalize_blocks(request['backend'],json.loads(raw_bytes),job['kind'])
            blocks = json.loads(json.dumps(blocks, ensure_ascii=False, default=encoder))
            row.update(status='PARTIAL_OUTPUT' if mode.get('producer_status','success')!='success' else 'SUCCEEDED', transcript='\n'.join(block['text'] for block in blocks),
                       raw_output_sha256=sha(raw_bytes), blocks=blocks, parameters=mode)
        except Exception as exc:
            row.update(status='FAILED', error=type(exc).__name__ + ': ' + str(exc))
        row['elapsed_seconds'] = time.monotonic() - started
        (output / (job['job_id'] + '.row.json')).write_text(json.dumps(row, ensure_ascii=False, indent=2), encoding='utf-8')
        print(job['job_id'], row['status'], flush=True)
    progress('COMPLETE')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
