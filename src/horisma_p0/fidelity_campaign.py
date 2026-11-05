"""Owned sequential offline experiments with frozen inputs and explicit failure budgets."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

import yaml

from .probe_artifacts import seal_attempt
from .research_slice import check_slice, encoded, read, sha

LOCK = 'spec/extensions/fidelity_campaign_v1.lock.json'
PROTOCOL = 'spec/extensions/fidelity_campaign_v1.yaml'


def load_suite(root, manifest_path):
    root, manifest_path = Path(root).resolve(), Path(manifest_path).resolve()
    lock = json.loads(read(root, LOCK)); raw = manifest_path.read_bytes(); suite = json.loads(raw)
    if (not manifest_path.is_relative_to(root / 'outputs/fidelity-suites')
            or manifest_path.parent.name != sha(raw) or lock['suite_id'] != sha(raw)):
        raise ValueError('UNFROZEN_OR_CHANGED_SUITE')
    protocol_raw = read(root, PROTOCOL); protocol = yaml.safe_load(protocol_raw)
    if sha(protocol_raw) != lock['protocol_sha256'] or sha(read(root, protocol['challenge'])) != lock['challenge_sha256']:
        raise ValueError('FROZEN_DEFINITION_CHANGED')
    if not check_slice(root, root / suite['base_slice_path'])['preview_eligible']:
        from .publication_rebase import effective_suite_base
        suite['effective_base_slice_path'] = effective_suite_base(root, suite)
    for name, digest in suite['artifacts'].items():
        if Path(name).name != name or sha((manifest_path.parent / name).read_bytes()) != digest:
            raise ValueError('FROZEN_INPUT_CHANGED')
    return suite, protocol


def run_backend(root, manifest_path, backend):
    root, manifest_path = Path(root).resolve(), Path(manifest_path).resolve()
    suite, protocol = load_suite(root, manifest_path)
    if backend not in protocol['backends'] or backend in protocol['excluded_backends']:
        raise ValueError('UNAPPROVED_CAMPAIGN_BACKEND')
    settings = protocol['backends'][backend]; budget = protocol['budgets']
    directory = root / 'outputs/fidelity-campaigns' / backend
    output = directory / 'runs' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output.mkdir(parents=True, exist_ok=False)
    model_path = '.rebuild/fidelity-models/manifest.json'
    model_raw = read(root, model_path)
    (output/'model-manifest.json').write_bytes(model_raw)
    model_path=(output/'model-manifest.json').relative_to(root).as_posix()
    worker_path = 'scripts/fidelity_backend_worker.py'
    (output/'worker-source.py').write_bytes(read(root,worker_path))
    (output/'normalizer-source.py').write_bytes(read(root,'src/horisma_p0/fidelity_blocks.py'))
    (output/'operator-source.py').write_bytes(Path(__file__).read_bytes())
    token = uuid.uuid4().hex
    # Labels, printed expectations, context answers and historical probes are deliberately absent.
    request = {'suite_id': manifest_path.parent.name, 'backend': backend, 'backend_version': settings['version'],
               'owner_token': token, 'worker_sha256': sha(read(root, worker_path)),
               'normalizer_sha256': sha(read(root, 'src/horisma_p0/fidelity_blocks.py')),
               'model_manifest_path': model_path, 'model_manifest_sha256': sha(model_raw),
               'jobs': [{'job_id': job['job_id'], 'kind': job['kind'], 'png_sha256': job['png_sha256'],
                         'png_path': (manifest_path.parent / job['png_path']).relative_to(root).as_posix()}
                        for job in suite['jobs']]}
    raw = encoded(request); (output / 'request.json').write_bytes(raw)
    env = {key: value for key, value in os.environ.items() if not key.startswith('MINERU_') and key not in {
        'GH_TOKEN', 'GITHUB_TOKEN', 'OPENAI_API_KEY', 'GOOGLE_API_KEY', 'GEMINI_API_KEY',
        'ANTHROPIC_API_KEY', 'HF_TOKEN', 'HUGGING_FACE_HUB_TOKEN'}}
    env.update(MINERU_HOME=str(root / '.rebuild/tools/mineru/home'),
               MINERU_CONFIG=str(root / '.rebuild/tools/mineru/campaign-config.yaml'),
               MINERU_MODEL_SOURCE='local', MINERU_MODEL_SMALL_BACKEND='onnx', MINERU_MODEL_ONNX_DEVICE='cpu',
               MINERU_TELEMETRY_DISABLED='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
               HF_HUB_DISABLE_TELEMETRY='1', HF_HUB_DISABLE_IMPLICIT_TOKEN='1', PYTHONIOENCODING='utf-8')
    lease_path = root / 'ops/state/research-model-screen.lock'; lease_path.parent.mkdir(parents=True, exist_ok=True)
    lease = lease_path.open('x'); process = None; started_jobs = []
    report = {'backend': backend, 'suite_id': manifest_path.parent.name, 'request_sha256': sha(raw),
              'operator_sha256': sha(Path(__file__).read_bytes()), 'budgets': budget,
              'status': 'UNRUN', 'scientific_acceptance': False, 'fidelity_qualified': False}
    started = time.monotonic(); phase_started = started; last_phase = None
    try:
        lease.write(json.dumps({'owner_token': token, 'run': str(output), 'backend': backend})); lease.flush()
        command = [str(root / settings['runtime']), str(root / worker_path), '--request', str(output / 'request.json'),
                   '--request-sha256', sha(raw)]
        with (output / 'stdout.txt').open('wb') as stdout, (output / 'stderr.txt').open('wb') as stderr:
            process = subprocess.Popen(command, cwd=root, env=env, stdout=stdout, stderr=stderr)
            while process.poll() is None:
                now = time.monotonic(); progress_path = output / 'progress.json'
                if progress_path.exists():
                    try:
                        progress = json.loads(progress_path.read_bytes())
                    except OSError:
                        progress = None
                    except ValueError:
                        report['status']='INVALID_PROGRESS';break
                    if progress is not None:
                        if (not isinstance(progress,dict) or not {'owner_token','phase','job_id'}<=set(progress)
                                or not isinstance(progress['phase'],str)
                                or progress['phase'] not in {'INITIALIZING','RUNNING','COMPLETE'}
                                or (progress['phase']=='RUNNING' and not isinstance(progress['job_id'],str))):
                            report['status']='INVALID_PROGRESS';break
                        if progress['owner_token'] != token:
                            report['status'] = 'FOREIGN_PROGRESS'; break
                        phase = (progress['phase'], progress['job_id'])
                        if phase != last_phase:
                            last_phase = phase; phase_started = now
                            if phase[0] == 'RUNNING':
                                if phase[1] not in {job['job_id'] for job in request['jobs']}:
                                    report['status'] = 'UNKNOWN_PROGRESS_JOB'; break
                                started_jobs.append(phase[1])
                            print(backend, phase[0], phase[1] or '', flush=True)
                limit = budget['max_job_seconds'] if last_phase and last_phase[0] == 'RUNNING' else budget['max_initialization_seconds']
                if now - started > budget['max_backend_seconds'] or now - phase_started > limit:
                    report.update(status='TIMEOUT', timed_out_phase=last_phase); break
                time.sleep(.1)
            if process.poll() is None:
                process.kill(); process.wait(timeout=15)
            report['process_returncode'] = process.returncode
            if report['status'] == 'UNRUN':
                report['status'] = 'PROCESS_COMPLETED' if process.returncode == 0 else 'PROCESS_FAILED'
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        report.update(status='LAUNCH_OR_MONITOR_FAILED', error=type(exc).__name__ + ': ' + str(exc))
    finally:
        if process is not None and process.poll() is None:
            process.kill(); process.wait(timeout=15)
        lease.close()
        try:
            current = json.loads(lease_path.read_bytes())
            if current.get('owner_token') == token:
                lease_path.unlink(); report['lease_cleanup'] = 'OWNED_LEASE_REMOVED'
            else:
                report['lease_cleanup'] = 'FOREIGN_LEASE_RETAINED'
        except (OSError, ValueError) as exc:
            report['lease_cleanup'] = 'UNVERIFIED'; report['cleanup_error'] = str(exc)
    completed_ids={job['job_id'] for job in request['jobs'] if (output/(job['job_id']+'.row.json')).is_file()}
    started_jobs=[job['job_id'] for job in request['jobs'] if job['job_id'] in completed_ids or job['job_id'] in started_jobs]
    if report['status']=='PROCESS_COMPLETED' and len(completed_ids)!=len(request['jobs']):
        report['status']='INCOMPLETE_OUTPUT'
    report.update(elapsed_seconds=time.monotonic() - started, started_jobs=started_jobs,
                  unrun_jobs=[job['job_id'] for job in request['jobs'] if job['job_id'] not in started_jobs])
    files = {path.name: path.read_bytes() for path in output.iterdir() if path.is_file() and path.suffix != '.pending'}
    files['process.json'] = encoded(report)
    attempt = seal_attempt(directory, manifest_path.parent.name, files)
    return {'backend': backend, 'status': report['status'], 'attempt_id': attempt,
            'started': len(started_jobs), 'planned': len(suite['jobs']), 'unrun': len(report['unrun_jobs']),
            'output': str(output), 'scientific_acceptance': False}
