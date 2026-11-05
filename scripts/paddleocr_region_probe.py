"""Isolated CPU PaddleOCR literal screen; historical input is conditional, private."""
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
import sys
import time
from difflib import SequenceMatcher
from datetime import datetime, timezone


def digest(body):
    return hashlib.sha256(body).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-id', choices=['1', '2', '3', '4', '5'], required=True)
    parser.add_argument('--lease-token', required=True)
    parser.add_argument('--slice', type=Path, required=True)
    parser.add_argument('--slice-sha256', required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root / 'src'))
    from horisma_p0.literal_controls import render_control, screen_passed
    from horisma_p0.probe_artifacts import seal_attempt
    from PIL import ImageFont

    folder = args.slice.resolve()
    if not folder.is_relative_to(root / 'outputs/research-slices'):
        raise ValueError('EXTERNAL_SLICE')
    raw_slice = (folder / 'slice.json').read_bytes()
    if digest(raw_slice) != args.slice_sha256:
        raise ValueError('CORRUPT_SLICE')
    payload = json.loads(raw_slice)
    source = payload['sources'][args.source_id]
    corpus_raw = (root / 'spec/examples/visual_literal_challenge.json').read_bytes()
    config = json.loads(corpus_raw)
    cases = config['cases']
    if len(cases) != 12 or config['policy']['required_matches'] != 12:
        raise ValueError('FROZEN_CONTROL_COUNT_REQUIRED')
    if (len({case['id'] for case in cases}) != len(cases)
            or any(case.get('synthetic') is not True or not re.fullmatch(r'[a-z][a-z0-9-]*', case['id']) for case in cases)):
        raise ValueError('UNIQUE_SAFE_SYNTHETIC_CONTROLS_REQUIRED')
    font_path = Path(config['font'])
    font = ImageFont.truetype(str(font_path), config['font_size'])
    images = [render_control(case, config, font) for case in cases]
    model_root = root / '.rebuild/tools/paddleocr/models'
    model_raw = (model_root / 'manifest.json').read_bytes()
    models = json.loads(model_raw)
    directories = {}
    for entry in models['models']:
        directory = (root / entry['path']).resolve()
        if not directory.is_relative_to(model_root):
            raise ValueError('EXTERNAL_MODEL_DIRECTORY')
        for name, info in entry['files'].items():
            if Path(name).name != name or digest((directory / name).read_bytes()) != info['sha256']:
                raise ValueError('MODEL_FILE_CHANGED')
        directories[entry['repository'].split('/')[-1]] = str(directory)

    output = root / 'outputs/parser-comparison/paddleocr-3.7.0'
    run = output / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    run.mkdir(parents=True, exist_ok=False)
    report = {'tool': 'paddleocr', 'version': '3.7.0', 'source_id': args.source_id,
              'source_sha256': source['sha256'], 'slice_id': folder.name,
              'pdf_page_index': payload['regions'][args.source_id]['page_index'],
              'corpus_sha256': digest(corpus_raw), 'font_sha256': digest(font_path.read_bytes()),
              'model_manifest_sha256': digest(model_raw), 'models': models,
              'script_sha256': digest(Path(__file__).read_bytes()), 'device': 'cpu',
              'control_helper_sha256': digest((root / 'src/horisma_p0/literal_controls.py').read_bytes()),
              'slice_sha256': args.slice_sha256,
              'controls': [], 'real_regions': [], 'status': 'UNRUN',
              'fidelity_qualified': False, 'historical_qualification': False,
              'scientific_acceptance': False,
              'release_authorized': False, 'network_policy': 'PYTHON_SOCKET_CONNECT_BLOCKED',
              'lineage_limit': 'Different v5 English weights; shared PaddleOCR lineage with RapidOCR v6 is possible'}
    files = {}

    def checkpoint():
        body = json.dumps(report, sort_keys=True, indent=2).encode()
        (run / 'report.json').write_bytes(body)
        return body

    os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['PADDLE_PDX_CACHE_HOME'] = str(root / '.rebuild/tools/paddleocr/cache')

    def block_network(event, _args):
        if event == 'socket.connect':
            raise OSError('OFFLINE_PROBE_NETWORK_BLOCKED')

    sys.addaudithook(block_network)
    lock = root / 'ops/state/research-model-screen.lock'
    lease = lock.open('x')
    started = time.monotonic()
    try:
        lease.write(json.dumps({'owner_token': args.lease_token, 'run': str(run)})); lease.flush()
        report['phase'] = 'IMPORT_AND_INITIALIZE'; checkpoint()
        from importlib.metadata import version
        report['runtime_versions'] = {name: version(name) for name in ('paddleocr', 'paddlepaddle', 'paddlex')}
        if report['runtime_versions']['paddleocr'] != '3.7.0' or report['runtime_versions']['paddlepaddle'] != '3.3.1':
            raise ValueError('PINNED_RUNTIME_REQUIRED')
        from paddleocr import PaddleOCR
        pipeline = PaddleOCR(
            text_detection_model_name='PP-OCRv5_mobile_det',
            text_detection_model_dir=directories['PP-OCRv5_mobile_det'],
            text_recognition_model_name='en_PP-OCRv5_mobile_rec',
            text_recognition_model_dir=directories['en_PP-OCRv5_mobile_rec'],
            use_doc_orientation_classify=False, use_doc_unwarping=False,
            use_textline_orientation=False, device='cpu', enable_mkldnn=False, cpu_threads=4)
        report['phase'] = 'SYNTHETIC_CONTROLS'; checkpoint()
        for case, png in zip(cases, images):
            path = run / (case['id'] + '.png'); path.write_bytes(png)
            tick = time.monotonic()
            result = list(pipeline.predict(str(path)))
            if len(result) != 1:
                raise ValueError('ONE_IMAGE_RESULT_REQUIRED')
            raw = json.dumps(result[0].json, ensure_ascii=False, indent=2).encode()
            (run / (case['id'] + '.json')).write_bytes(raw)
            files[case['id'] + '.png'] = png; files[case['id'] + '.json'] = raw
            parsed = json.loads(raw)['res']
            transcript = ' '.join(parsed['rec_texts'])
            row = {'id': case['id'], 'synthetic': True, 'expected': case['text'],
                   'transcript': transcript, 'image_sha256': digest(png), 'raw_output_sha256': digest(raw),
                   'literal_match': ' '.join(transcript.split()) == case['text'],
                   'elapsed_seconds': time.monotonic() - tick}
            report['controls'].append(row); checkpoint()
            print(case['id'], row['literal_match'], flush=True)
            if not row['literal_match']:
                break
        passed = screen_passed(report['controls'], 12)
        report['status'] = 'PASSED_DIAGNOSTIC_ONLY' if passed else 'FAILED_LITERAL_SCREEN'
        if passed:
            report['phase'] = 'HISTORICAL_REGION_DIAGNOSTIC'; checkpoint()
            region = payload['regions'][args.source_id]

            def preserved(blob):
                path = (root / blob['path']).resolve()
                if not path.is_relative_to(root / 'data/intake/derived/evidence-vault'):
                    raise ValueError('EXTERNAL_PRESERVED_INPUT')
                body = path.read_bytes()
                if digest(body) != blob['sha256']:
                    raise ValueError('PRESERVED_INPUT_CHANGED')
                return body

            if digest(preserved(source['preserved_blob'])) != source['sha256']:
                raise ValueError('SOURCE_VERSION_CHANGED')
            png = preserved(region['render_blob'])
            native = preserved(region['native_text_blob']).decode('utf-8')
            path = run / 'historical-region.png'; path.write_bytes(png)
            files['historical-region.png'] = png
            tick = time.monotonic()
            result = list(pipeline.predict(str(path)))
            if len(result) != 1:
                raise ValueError('ONE_REGION_RESULT_REQUIRED')
            raw = json.dumps(result[0].json, ensure_ascii=False, indent=2).encode()
            files['historical-region.json'] = raw
            (run / 'historical-region.json').write_bytes(raw)
            transcript = '\n'.join(json.loads(raw)['res']['rec_texts'])
            report['real_regions'].append({
                'region_id': region['region_id'], 'image_sha256': digest(png),
                'native_text_sha256': digest(native.encode('utf-8')), 'raw_output_sha256': digest(raw),
                'region_pdf_points': region['region_pdf_points'], 'normalized_region': region['normalized_region'],
                'transcript': transcript, 'native_text': native,
                'whitespace_folded_agreement': SequenceMatcher(None, ' '.join(native.split()), ' '.join(transcript.split())).ratio(),
                'agreement_scope': 'DIAGNOSTIC_NOT_FIDELITY', 'fidelity_qualified': False,
                'elapsed_seconds': time.monotonic() - tick})
            report['real_region_status'] = 'PROPOSED_UNQUALIFIED'
        else:
            report['real_region_status'] = 'ABSTAINED_FAILED_CONTROL'
    except Exception as exc:
        report.update(status='FAILED', failed_phase=report.get('phase'), error=type(exc).__name__ + ': ' + str(exc))
    finally:
        lease.close(); lock.unlink(missing_ok=True)
    report['unrun_controls'] = [case['id'] for case in cases[len(report['controls']):]]
    report['elapsed_seconds'] = time.monotonic() - started
    report['phase'] = 'FINISHED'
    files['receipt.json'] = checkpoint()
    attempt = seal_attempt(output, args.source_id, files)
    print(json.dumps({'report': str(run / 'report.json'), 'attempt_id': attempt,
                      'status': report['status'], 'attempted': len(report['controls']),
                      'planned': 12, 'unrun': len(report['unrun_controls']), 'fidelity_qualified': False}))
    return 0 if report['status'] == 'PASSED_DIAGNOSTIC_ONLY' else 1


if __name__ == '__main__':
    raise SystemExit(main())
