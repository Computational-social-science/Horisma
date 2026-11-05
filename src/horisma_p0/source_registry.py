"""Additional user-supplied PDFs enter the same custody/readings lane, not frozen P0."""
import json
from pathlib import Path

from .research_slice import check_slice, encoded, preserve_blob, read, sha, write_new

REGISTRY = 'data/intake/derived/additional-documents'


def register_pdf(root, path):
    import pymupdf
    root, path = Path(root).resolve(), Path(path).resolve()
    if not path.is_relative_to(root) or path.suffix.lower() != '.pdf': raise ValueError('LOCAL_PROJECT_PDF_REQUIRED')
    relative = path.relative_to(root).as_posix(); raw = read(root, relative); digest = sha(raw)
    with pymupdf.open(stream=raw, filetype='pdf') as doc:
        if doc.needs_pass: raise ValueError('AUTHORIZED_UNLOCKED_SOURCE_REQUIRED')
        count = len(doc); metadata = doc.metadata
    ident = 'local-'+digest
    work = 'horisma:work:unresolved-intake-'+sha(relative.encode())[:20]
    record = {'source_id': ident, 'path': relative, 'sha256': digest, 'work_id': work,
              'version_id': work+'@'+digest, 'preserved_blob': preserve_blob(root, raw, 'SOURCE_VERSION'),
              'pdf_page_count': count, 'pdf_metadata': metadata, 'provided_filename': path.name,
              'identity_status': 'UNRESOLVED_INTAKE_ID_NOT_BIBLIOGRAPHIC_ADJUDICATION',
              'historical_date_from_filename': None, 'scientific_acceptance': False}
    output = root/REGISTRY/(ident+'.json'); write_new(output, encoded(record))
    return {'source_id': ident, 'record': output.relative_to(root).as_posix(), 'pdf_pages': count,
            'scientific_acceptance': False}


def document_source(root, source_id):
    root = Path(root).resolve()
    if source_id.startswith('local-'):
        if len(source_id) != 70 or any(c not in '0123456789abcdef' for c in source_id[6:]):
            raise ValueError('INVALID_LOCAL_SOURCE_ID')
        record = json.loads(read(root, REGISTRY+'/'+source_id+'.json'))
        if record['source_id'] != source_id or record['sha256'] != source_id[6:]:
            raise ValueError('LOCAL_SOURCE_BINDING_CHANGED')
        if sha(read(root, record['preserved_blob']['path'])) != record['sha256']:
            raise ValueError('LOCAL_SOURCE_BYTES_CHANGED')
        return record
    head = json.loads(read(root, 'ops/state/research-slice-head.json'))
    if not check_slice(root, root/head['slice'])['preview_eligible']: raise ValueError('STALE_DOCUMENT_BASE')
    raw = read(root, head['slice']+'/slice.json')
    if sha(raw) != head['sha256']: raise ValueError('DOCUMENT_BASE_CHANGED')
    sources = json.loads(raw)['sources']
    if source_id not in sources: raise ValueError('UNKNOWN_DOCUMENT_SOURCE')
    return sources[source_id]
