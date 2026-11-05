"""Pinned offline full-PDF adapter. Never marks text scientifically qualified."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--request', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    args = parser.parse_args(); root = Path(__file__).resolve().parents[1]
    raw = args.request.read_bytes(); request = json.loads(raw); output = args.request.parent
    if digest(raw) != args.sha256 or not output.resolve().is_relative_to(root/'outputs/full-document-ocr/runs'):
        raise ValueError('UNBOUND_DOCUMENT_REQUEST')
    if digest(Path(__file__).read_bytes()) != request['worker_sha256']:
        raise ValueError('DOCUMENT_WORKER_CHANGED')
    adapter = root/'scripts/fidelity_backend_worker.py'
    if digest(adapter.read_bytes()) != request['adapter_sha256']:
        raise ValueError('DOCUMENT_ADAPTER_CHANGED')
    models = (output/'model-manifest.json').read_bytes()
    if digest(models) != request['model_manifest_sha256']: raise ValueError('MODEL_MANIFEST_CHANGED')
    for name, info in json.loads(models)['backend_files']['docling'].items():
        path = Path(name) if Path(name).is_absolute() else root/name
        if digest(path.read_bytes()) != info['sha256']: raise ValueError('DOCUMENT_MODEL_CHANGED')
    source = output/'input.pdf'
    if digest(source.read_bytes()) != request['source_sha256']: raise ValueError('DOCUMENT_INPUT_CHANGED')
    os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1')

    def offline(event, _args):
        if event == 'socket.connect': raise OSError('DOCUMENT_NETWORK_DISABLED')
    sys.addaudithook(offline)
    from importlib.metadata import version
    if version('docling') != request['docling_version']: raise ValueError('DOCLING_VERSION_CHANGED')
    import torch
    import numpy as np
    torch.manual_seed(request['seed']); np.random.seed(request['seed'])
    from fidelity_backend_worker import make_adapter
    engine = make_adapter(root, 'docling')
    structured, parameters = engine(source, 'pdf')
    data = json.dumps(structured, ensure_ascii=False, indent=2).encode()
    (output/'document.raw.json').write_bytes(data)
    (output/'result.json').write_text(json.dumps({'producer_status': parameters['producer_status'],
        'parameters': parameters, 'input_kind': 'FULL_PDF', 'raw_sha256': digest(data),
        'source_sha256': request['source_sha256'], 'scientific_acceptance': False}), encoding='utf-8')


if __name__ == '__main__': main()
