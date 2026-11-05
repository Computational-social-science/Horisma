"""Pinned local anymd native-layout probe; never installs MCP clients or Pro."""
import argparse
import hashlib
import json
import os
import subprocess
import time
import sys
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source-id',choices=['1','2','3','4','5'],required=True)
    args=parser.parse_args();root=Path(__file__).resolve().parents[1]
    exe=root/'.rebuild/tools/anymd/node_modules/@sylphx/anymd-win32-x64-msvc/anymd.exe'
    if not exe.is_file():raise ValueError('PINNED_ANYMD_NOT_INSTALLED')
    import yaml
    config=yaml.safe_load((root/'spec/extensions/document_parsers.yaml').read_text(encoding='utf-8'))
    if hashlib.sha256(exe.read_bytes()).hexdigest()!=config['anymd']['binary_sha256']:raise ValueError('ANYMD_BINARY_CHANGED')
    head=json.loads((root/'ops/state/research-slice-head.json').read_bytes())
    folder=(root/head['slice']).resolve()
    if not folder.is_relative_to(root/'outputs/research-slices'):raise ValueError('EXTERNAL_SLICE')
    data=(folder/'slice.json').read_bytes()
    if hashlib.sha256(data).hexdigest()!=head['sha256']:raise ValueError('CORRUPT_SLICE')
    payload=json.loads(data);sid=args.source_id;source=payload['sources'][sid]
    raw=(root/source['preserved_blob']['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=source['sha256']:raise ValueError('STALE_SOURCE')
    out=root/'outputs/parser-comparison/anymd-8.5.9';out.mkdir(parents=True,exist_ok=True)
    path=out/('input-'+sid+'.pdf')
    if path.exists() and path.read_bytes()!=raw:raise ValueError('PROBE_INPUT_CONFLICT')
    if not path.exists():path.write_bytes(raw)
    command=[str(exe),str(path),'--pages',str(payload['regions'][sid]['page_index']+1),
             '--no-ocr','--images','none','--max-tokens','12000']
    env=dict(os.environ);env['ANYMD_CACHE_DIR']=str(out/'cache')
    start=time.monotonic()
    result=subprocess.run(command,capture_output=True,timeout=60,env=env)
    (out/(sid+'.md')).write_bytes(result.stdout)
    (out/(sid+'.stderr.txt')).write_bytes(result.stderr)
    receipt={'tool':'anymd','version':'8.5.9','source_sha256':source['sha256'],
             'source_id':sid,'pdf_page_index':payload['regions'][sid]['page_index'],
             'binary_sha256':hashlib.sha256(exe.read_bytes()).hexdigest(),'command':command,
             'exit_code':result.returncode,'elapsed_seconds':time.monotonic()-start,
             'output_sha256':hashlib.sha256(result.stdout).hexdigest(),
             'fidelity_qualified':False,'release_authorized':False}
    record=json.dumps(receipt,indent=2).encode('utf-8')
    (out/(sid+'.receipt.json')).write_bytes(record)
    sys.path.insert(0,str(root/'src'))
    from horisma_p0.probe_artifacts import seal_attempt
    seal_attempt(out,sid,{'receipt.json':record,'document.md':result.stdout})
    print(json.dumps(receipt));return result.returncode


if __name__=='__main__':raise SystemExit(main())
