"""Own and bound an isolated PaddleOCR process without changing automatic routes."""
import json
from pathlib import Path
import subprocess
import uuid

from .probe_artifacts import seal_attempt, load_attempt
from .research_slice import check_slice, encoded, sha, write_new
from .transcription_correction import signature


def diagnose_paddle_attempt(root, folder, source_id):
    """Compare a sealed candidate with native text; neither channel is ground truth."""
    root, folder = Path(root).resolve(), Path(folder).resolve()
    if not check_slice(root, folder)['preview_eligible']:
        raise ValueError('STALE_SLICE')
    payload = json.loads((folder / 'slice.json').read_bytes())
    attempt, files = load_attempt(root / 'outputs/parser-comparison/paddleocr-3.7.0', source_id)
    receipt = json.loads(files['receipt.json'])
    source, region = payload['sources'][source_id], payload['regions'][source_id]
    if (receipt['slice_id'] != folder.name or receipt['source_sha256'] != source['sha256']
            or receipt['pdf_page_index'] != region['page_index']):
        raise ValueError('STALE_PADDLE_ATTEMPT')
    rows = []
    for candidate in receipt['real_regions']:
        if (candidate['region_id'] != region['region_id']
                or candidate['image_sha256'] != region['render_blob']['sha256']
                or sha(files['historical-region.png']) != candidate['image_sha256']
                or sha(files['historical-region.json']) != candidate['raw_output_sha256']
                or sha(candidate['native_text'].encode()) != region['native_text_blob']['sha256']):
            raise ValueError('PADDLE_REGION_BINDING_CHANGED')
        parsed = json.loads(files['historical-region.json'])['res']
        if '\n'.join(parsed['rec_texts']) != candidate['transcript']:
            raise ValueError('PADDLE_TRANSCRIPT_CHANGED')
        before, after = signature(candidate['native_text']), signature(candidate['transcript'])
        differences = {key: {'native': before[key], 'image_ocr': after[key]}
                       for key in before if before[key] != after[key]}
        rows.append({'region_id': candidate['region_id'], 'critical_disagreements': differences,
                     'status': 'UNQUALIFIED_CRITICAL_DISAGREEMENTS' if differences else 'UNQUALIFIED_AGREEMENT',
                     'fidelity_qualified': False})
    report = {'slice_id': folder.name, 'attempt_id': attempt, 'source_id': source_id,
              'producer_script_sha256': receipt['script_sha256'],
              'diagnostic_code_sha256': sha(Path(__file__).read_bytes()),
              'signature_code_sha256': sha((root / 'src/horisma_p0/transcription_correction.py').read_bytes()),
              'rows': rows, 'affected_assertions': payload['assertions'], 'affected_tasks': payload['tasks'],
              'scope': 'NATIVE_AND_IMAGE_OCR_ARE_UNQUALIFIED_CHANNELS_NOT_TRUTH_LABELS',
              'fidelity_qualified': False, 'scientific_acceptance': False, 'release_authorized': False}
    raw = encoded(report)
    output = root / 'outputs/parser-comparison/paddle-diagnostics' / sha(raw) / 'report.json'
    write_new(output, raw)
    return {'report': str(output), 'regions': len(rows), 'fidelity_qualified': False}


def run_paddle_candidate(root, source_id):
    root = Path(root).resolve()
    head = json.loads((root / 'ops/state/research-slice-head.json').read_bytes())
    folder = (root / head['slice']).resolve()
    if not folder.is_relative_to(root / 'outputs/research-slices'):
        raise ValueError('EXTERNAL_SLICE')
    if sha((folder / 'slice.json').read_bytes()) != head['sha256']:
        raise ValueError('CORRUPT_SLICE')
    if not check_slice(root, folder)['preview_eligible']:
        raise ValueError('STALE_SLICE')
    token = uuid.uuid4().hex
    command = [str(root / '.rebuild/tools/paddleocr/venv/Scripts/python.exe'),
               str(root / 'scripts/paddleocr_region_probe.py'),
               '--source-id', source_id, '--lease-token', token,
               '--slice', str(folder), '--slice-sha256', head['sha256']]
    result = {'backend': 'paddleocr', 'phase': 'ISOLATED_LITERAL_SCREEN',
              'slice_id': folder.name, 'timeout_seconds': 150,
              'automatic_route_changed': False, 'fidelity_qualified': False,
              'scientific_acceptance': False, 'release_authorized': False}
    try:
        process = subprocess.run(command, cwd=root, capture_output=True, timeout=150)
        result.update(process_returncode=process.returncode, status='PROCESS_COMPLETED')
        stdout, stderr = process.stdout, process.stderr
    except subprocess.TimeoutExpired as exc:
        # subprocess.run kills and waits for its owned child before raising.
        result.update(process_returncode=124, status='PROCESS_TIMEOUT')
        stdout, stderr = exc.stdout or b'', exc.stderr or b''
        lock = root / 'ops/state/research-model-screen.lock'
        try:
            lease = json.loads(lock.read_bytes())
            if lease.get('owner_token') == token:
                lock.unlink()
                result['lease_cleanup'] = 'REMOVED_OWNED_TERMINATED_PROCESS_LEASE'
            else:
                result['lease_cleanup'] = 'FOREIGN_LEASE_UNCHANGED'
        except FileNotFoundError:
            result['lease_cleanup'] = 'NO_LEASE'
        except (OSError, ValueError) as cleanup:
            result['lease_cleanup'] = 'UNVERIFIED'
            result['cleanup_error'] = str(cleanup)
    result.update(stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))
    if result['process_returncode']==0:
        try:
            result['region_diagnostic']=diagnose_paddle_attempt(root,folder,source_id)
        except (OSError,ValueError,KeyError,TypeError) as exc:
            result.update(process_returncode=1,status='OUTPUT_QUARANTINED',error=str(exc))
    ident = seal_attempt(root / 'outputs/parser-comparison/paddleocr-processes', source_id,
                         {'receipt.json': encoded(result), 'stdout.txt': stdout, 'stderr.txt': stderr})
    return {**result, 'process_attempt_id': ident,
            'stdout_tail': stdout.decode('utf-8', errors='replace')[-1000:],
            'stderr_tail': stderr.decode('utf-8', errors='replace')[-700:]}
