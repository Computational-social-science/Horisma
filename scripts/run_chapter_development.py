"""Local-only development run. Private outputs; no benchmark accuracy claims."""
import json
import sys
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from horisma_p0.local_documents import NoModelRedirects
from horisma_p0.development_packets import extract_packet, build_prompt, validate_response, sha


def main():
    inputs = [ROOT/'spec/examples/matthew_chapter_one_map.json',
              ROOT/'data/benchmarks/development/matthew-role-provenance-v0.1/tasks.jsonl',
              ROOT/'data/intake/derived/scientist-profiles-v0.1/records.jsonl']
    mapping = json.loads(inputs[0].read_text(encoding='utf-8'))
    tasks = [json.loads(s) for s in inputs[1].read_text(encoding='utf-8').splitlines()]
    people = [json.loads(s) for s in inputs[2].read_text(encoding='utf-8').splitlines()]
    packets = {sid: extract_packet(ROOT, sid, source) for sid, source in mapping['sources'].items()}
    for task in tasks:
        if task['split'] != 'DEVELOPMENT_ONLY':
            raise ValueError('DEVELOPMENT_ONLY_REQUIRED')
        for sid, source in task['sources'].items():
            if source != mapping['sources'][sid]:
                raise ValueError('STALE_TASK_SOURCE')
    jobs = [(t['task_id'], t['question'], list(t['sources'])) for t in tasks]
    for person in people:
        for a in person['contributions']:
            sid = a['source_id']
            if a['source_binding'] != mapping['sources'][sid]:
                raise ValueError('STALE_ASSERTION_SOURCE')
            jobs.append((a['assertion_id'], 'Does the excerpt express this candidate proposition? ' + a['proposition'], [sid]))
    opener = build_opener(ProxyHandler({}), NoModelRedirects())
    with opener.open('http://127.0.0.1:8081/v1/models', timeout=5) as response:
        model = json.load(response)['data'][0]['id']
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = ROOT/'outputs/development-runs'/stamp
    output.mkdir(parents=True, exist_ok=False)
    (output/'packets.json').write_text(json.dumps(packets, ensure_ascii=False, indent=2), encoding='utf-8')
    manifest = {'input_sha256': {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for p in inputs},
                'script_sha256': sha(Path(__file__).read_bytes()),
                'operator_sha256': sha((ROOT/'src/horisma_p0/development_packets.py').read_bytes()),
                'model_id': model, 'started_at_utc': stamp, 'gold_labels': 0,
                'scientific_acceptance': False, 'release_authorized': False, 'results': []}
    for job_id, question, ids in jobs:
        prompt = build_prompt(question, [packets[sid] for sid in ids])
        body = {'model': model, 'messages': [{'role': 'user', 'content': prompt}],
                'temperature': 0, 'seed': 20261105, 'max_tokens': 450, 'stream': False,
                'chat_template_kwargs': {'enable_thinking': False},
                'response_format': {'type': 'json_schema', 'json_schema': {
                    'name': 'development_reading', 'strict': True, 'schema': {
                        'type': 'object', 'additionalProperties': False,
                        'required': ['answer', 'source_ids', 'abstained', 'limitations'],
                        'properties': {'answer': {'type': 'string'},
                            'source_ids': {'type': 'array', 'items': {'type': 'string', 'enum': ids}},
                            'abstained': {'type': 'boolean'},
                            'limitations': {'type': 'array', 'items': {'type': 'string'}}}}}}}
        record = {'id': job_id, 'packet_sha256': {sid: sha(json.dumps(packets[sid], sort_keys=True).encode()) for sid in ids},
                  'request': body, 'prompt_sha256': sha(prompt.encode()), 'score': None,
                  'scientific_status': 'ABSTAINED_UNQUALIFIED_FIDELITY_AND_REVIEW'}
        try:
            with opener.open(Request('http://127.0.0.1:8081/v1/chat/completions', data=json.dumps(body).encode(),
                                     headers={'Content-Type': 'application/json'}), timeout=45) as response:
                raw = response.read(512000)
            record['raw_response_sha256'] = sha(raw)
            record['raw_response_text'] = raw.decode('utf-8', errors='replace')
            record['raw_response'] = json.loads(raw)
            content = record['raw_response']['choices'][0]['message']['content']
            record['proposal'] = validate_response(content, set(ids))
            record['execution_status'] = 'SUCCEEDED' if record['proposal'] is not None else 'QUARANTINED_INVALID_OUTPUT'
        except (OSError, ValueError, KeyError, IndexError, TypeError) as exc:
            record.update(execution_status='FAILED', error=type(exc).__name__ + ': ' + str(exc))
        path = output/(sha(job_id.encode())[:16] + '.json')
        path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        manifest['results'].append({'id': job_id, 'file': path.name, 'sha256': sha(path.read_bytes()),
                                    'execution_status': record['execution_status']})
        (output/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(job_id, record['execution_status'], flush=True)
    print(output, flush=True)


if __name__ == '__main__':
    main()
