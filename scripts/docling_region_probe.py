"""Offline, page-limited Docling diagnostic; no scientific acceptance or upload."""
import argparse
import hashlib
import json
import os
import time
import sys
from pathlib import Path

os.environ['HF_HUB_OFFLINE']='1'
os.environ['TRANSFORMERS_OFFLINE']='1'
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--source-id',choices=['1','2','3','4','5'],required=True)
    parser.add_argument('--ocr-model-dir',type=Path,required=True)
    parser.add_argument('--device',choices=['cuda','cpu'],default='cuda')
    args=parser.parse_args();root=args.root.resolve()
    import importlib.metadata
    from docling.document_converter import DocumentConverter,PdfFormatOption
    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions,RapidOcrOptions
    from docling.datamodel.accelerator_options import AcceleratorOptions,AcceleratorDevice
    version=importlib.metadata.version('docling')
    head=json.loads((root/'ops/state/research-slice-head.json').read_bytes())
    folder=(root/head['slice']).resolve()
    if not folder.is_relative_to(root/'outputs/research-slices'):raise ValueError('EXTERNAL_SLICE')
    raw=(folder/'slice.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=head['sha256']:raise ValueError('CORRUPT_SLICE')
    payload=json.loads(raw);sid=args.source_id;source=payload['sources'][sid]
    original=root/source['preserved_blob']['path'];data=original.read_bytes()
    if hashlib.sha256(data).hexdigest()!=source['sha256']:raise ValueError('SOURCE_VERSION_MISMATCH')
    out=root/'outputs/parser-comparison'/('docling-'+version);out.mkdir(parents=True,exist_ok=True)
    src=out/('input-'+sid+'.pdf')
    if src.exists() and src.read_bytes()!=data:raise ValueError('INPUT_PROBE_CONFLICT')
    if not src.exists():src.write_bytes(data)
    models=args.ocr_model_dir.resolve()
    model_paths={k:models/name for k,name in {'det_model_path':'PP-OCRv6_det_small.onnx','rec_model_path':'PP-OCRv6_rec_small.onnx','cls_model_path':'ch_ppocr_mobile_v2.0_cls_mobile.onnx'}.items()}
    if not all(p.is_file() for p in model_paths.values()):raise ValueError('LOCAL_OCR_MODELS_MISSING')
    options=PdfPipelineOptions(do_ocr=True,do_table_structure=False,enable_remote_services=False,document_timeout=90)
    options.ocr_options=RapidOcrOptions(backend='onnxruntime',lang=['en'],**{k:str(p) for k,p in model_paths.items()})
    options.accelerator_options=AcceleratorOptions(device=AcceleratorDevice(args.device),num_threads=4)
    start=time.monotonic()
    record={'tool':'docling','version':version,'source_id':sid,'source_sha256':source['sha256'],
            'pdf_page_index':payload['regions'][sid]['page_index'],'offline':True,
            'options':options.model_dump(mode='json'),'fidelity_qualified':False,'release_authorized':False,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    lock=root/'ops/state/research-model-screen.lock';lock.parent.mkdir(parents=True,exist_ok=True)
    lease=lock.open('x');lease.write('Docling page probe '+sid);lease.flush()
    try:
        converter=DocumentConverter(format_options={InputFormat.PDF:PdfFormatOption(pipeline_options=options)})
        page=record['pdf_page_index']+1
        result=converter.convert(src,page_range=(page,page))
        markdown=result.document.export_to_markdown()
        structured=result.document.export_to_dict()
        markdown_bytes=markdown.encode('utf-8')
        structured_bytes=json.dumps(structured,ensure_ascii=False,indent=2).encode('utf-8')
        (out/(sid+'.md')).write_bytes(markdown_bytes)
        (out/(sid+'.document.json')).write_bytes(structured_bytes)
        record.update(status=result.status.value,markdown_sha256=hashlib.sha256(markdown.encode()).hexdigest(),
                      structure_sha256=hashlib.sha256(structured_bytes).hexdigest(),
                      text_items=len(structured.get('texts',[])),errors=[str(e) for e in result.errors])
    except Exception as exc:
        record.update(status='FAILED',error=type(exc).__name__+': '+str(exc))
    finally:
        lease.close();lock.unlink(missing_ok=True)
    record['elapsed_seconds']=time.monotonic()-start
    receipt=json.dumps(record,indent=2).encode('utf-8')
    (out/(sid+'.receipt.json')).write_bytes(receipt)
    sys.path.insert(0,str(root/'src'))
    from horisma_p0.probe_artifacts import seal_attempt
    files={'receipt.json':receipt}
    if record['status']=='success':files.update({'document.md':markdown_bytes,'document.json':structured_bytes})
    seal_attempt(out,sid,files)
    print(json.dumps({k:record.get(k) for k in ['version','source_id','status','text_items','elapsed_seconds','error']}),flush=True)
    return 1 if record['status']=='FAILED' or record['status']=='failure' else 0


if __name__=='__main__':raise SystemExit(main())
