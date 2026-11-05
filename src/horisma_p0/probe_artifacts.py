"""Immutable parser attempts and atomic heads, with only standard-library dependencies."""
import hashlib
import json
import os
import tempfile
from pathlib import Path


def seal_attempt(directory,source_id,files):
    directory=Path(directory)
    hashes={name:hashlib.sha256(body).hexdigest() for name,body in files.items()}
    manifest=json.dumps({'source_id':source_id,'files':hashes},sort_keys=True).encode()
    ident=hashlib.sha256(manifest).hexdigest();folder=directory/'attempts'/ident
    folder.mkdir(parents=True,exist_ok=True)
    for name,body in {**files,'manifest.json':manifest}.items():
        if Path(name).name!=name:raise ValueError('ATTEMPT_FILENAME_REQUIRED')
        target=folder/name
        if target.exists():
            if target.read_bytes()!=body:raise ValueError('ATTEMPT_CONFLICT')
            continue
        fd,temp=tempfile.mkstemp(prefix='.pending-',dir=folder)
        try:
            with os.fdopen(fd,'wb') as stream:stream.write(body);stream.flush();os.fsync(stream.fileno())
            if os.name=='nt':os.rename(temp,target)
            else:os.link(temp,target)
        finally:Path(temp).unlink(missing_ok=True)
    fd,temp=tempfile.mkstemp(prefix='.head-',dir=directory)
    with os.fdopen(fd,'wb') as stream:stream.write(json.dumps({'attempt_id':ident}).encode());stream.flush();os.fsync(stream.fileno())
    os.replace(temp,directory/(source_id+'.head.json'))
    return ident


def load_attempt(directory,source_id):
    directory=Path(directory).resolve();head=json.loads((directory/(source_id+'.head.json')).read_bytes())
    folder=(directory/'attempts'/head['attempt_id']).resolve()
    if not folder.is_relative_to(directory/'attempts'):raise ValueError('EXTERNAL_PARSER_ATTEMPT')
    raw=(folder/'manifest.json').read_bytes()
    if hashlib.sha256(raw).hexdigest()!=head['attempt_id']:raise ValueError('ATTEMPT_MANIFEST_CHANGED')
    manifest=json.loads(raw)
    if manifest['source_id']!=source_id:raise ValueError('WRONG_ATTEMPT_SOURCE_ID')
    files={}
    for name,digest in manifest['files'].items():
        if Path(name).name!=name:raise ValueError('INVALID_ATTEMPT_FILENAME')
        body=(folder/name).read_bytes()
        if hashlib.sha256(body).hexdigest()!=digest:raise ValueError('PARSER_OUTPUT_CHANGED')
        files[name]=body
    return head['attempt_id'],files
