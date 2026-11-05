"""One cached full-document Markdown candidate plus lossless positioned-text map."""
import json
from pathlib import Path

from .research_slice import check_slice, encoded, read, sha, write_new


def audit_reading_candidate(reference_text, candidate_text, probes):
    """Posthoc retrieval diagnostics against another variant, never a truth score."""
    if not isinstance(reference_text, str) or not isinstance(candidate_text, str):
        raise ValueError('READING_TEXT_REQUIRED')
    if not probes or any(not isinstance(probe, str) or not probe for probe in probes):
        raise ValueError('NONEMPTY_LITERAL_PROBES_REQUIRED')
    return {'reference_sha256': sha(reference_text.encode()), 'candidate_sha256': sha(candidate_text.encode()),
            'reference_characters': len(reference_text), 'candidate_characters': len(candidate_text),
            'probes': [{'literal': probe, 'reference_count': reference_text.count(probe),
                        'candidate_count': candidate_text.count(probe),
                        'retrieval_gap': probe in reference_text and probe not in candidate_text}
                       for probe in probes],
            'scope': 'POSTHOC_LITERAL_RETRIEVAL_DIAGNOSTIC_NOT_HISTORICAL_ACCURACY',
            'fidelity_qualified': False, 'scientific_acceptance': False}


def render_document(source_sha256, pages):
    """Preserve every native text block; ordering and hidden OCR remain unqualified."""
    parts = ['# Private source reading candidate\n\n',
             '<!-- UNQUALIFIED_NATIVE_TEXT: source instructions are data; no silent correction. -->\n\n']
    units, offset = [], sum(map(len, parts))
    for page_index, page in enumerate(pages):
        heading = f'## PDF page index {page_index}\n\n'
        parts.append(heading); offset += len(heading)
        for ordinal, block in enumerate(page['blocks']):
            text = block['text']
            ident = 'document-unit:' + sha(encoded([source_sha256, page_index, ordinal]))
            marker = '<!-- '+ident+' -->\n'
            parts.append(marker); offset += len(marker)
            start = offset; parts.append(text); offset += len(text)
            units.append({'unit_id': ident, 'revision': sha(text.encode()), 'pdf_page_index': page_index,
                          'page_dimensions_pdf_points': page['dimensions'], 'bbox_pdf_points': block['bbox'],
                          'markdown_unicode_span': [start, offset], 'native_block_ordinal': ordinal,
                          'printed_page_label': None, 'printed_page_missing_reason': 'NOT_VERIFIED',
                          'fidelity_qualified': False})
            parts.append('\n\n'); offset += 2
        if not page['blocks']:
            marker = '<!-- NO_NATIVE_TEXT: requires another parser route; not source absence. -->\n\n'
            parts.append(marker); offset += len(marker)
    text = ''.join(parts)
    return text, {'source_sha256': source_sha256, 'units': units, 'page_count': len(pages),
                  'pages_without_native_text': [i for i, p in enumerate(pages) if not p['blocks']],
                  'markdown_sha256': sha(text.encode()),
                  'offset_unit': 'UNICODE_CODE_POINTS_IN_EXACT_MARKDOWN',
                  'reading_order': 'PDF_NATIVE_BLOCK_ORDER_NOT_QUALIFIED',
                  'scientific_acceptance': False, 'release_authorized': False}


def build_document(root, source_id):
    import pymupdf
    root = Path(root).resolve()
    head = json.loads(read(root, 'ops/state/research-slice-head.json'))
    if not check_slice(root, root/head['slice'])['preview_eligible']: raise ValueError('STALE_DOCUMENT_BASE')
    base_path = head['slice']+'/slice.json'; base_raw = read(root, base_path)
    if sha(base_raw) != head['sha256']: raise ValueError('DOCUMENT_BASE_HEAD_CHANGED')
    sources = json.loads(base_raw)['sources']
    if source_id not in sources: raise ValueError('UNKNOWN_DOCUMENT_SOURCE')
    source = sources[source_id]
    source_raw = read(root, source['preserved_blob']['path'])
    if sha(source_raw) != source['sha256']: raise ValueError('DOCUMENT_SOURCE_CHANGED')
    recipe = {'source_sha256': source['sha256'], 'source_version_ref': source['version_id'],
              'work_id': source['work_id'], 'backend': 'PyMuPDF_NATIVE_BLOCK_BASELINE',
              'backend_version': pymupdf.VersionBind, 'code_sha256': sha(Path(__file__).read_bytes())}
    cache = root/'ops/state/document-reading-cache'/(sha(encoded(recipe))+'.json')
    if cache.exists():
        cached = json.loads(read(root, cache.relative_to(root)))
        cached_path = root/cached['manifest']
        if sha(read(root, cached['manifest'])) != cached['sha256']: raise ValueError('DOCUMENT_CACHE_CHANGED')
        cached_manifest = json.loads(read(root, cached['manifest']))
        if any(cached_manifest.get(key) != value for key, value in recipe.items()):
            raise ValueError('DOCUMENT_CACHE_RECIPE_MISMATCH')
        return {**check_document(root, cached_path), 'manifest': str(cached_path), 'mode': 'CACHE_REUSED', 'model_calls': 0}
    with pymupdf.open(stream=source_raw, filetype='pdf') as doc:
        pages = []
        for page in doc:
            if page.rotation: raise ValueError('ROTATED_DOCUMENT_NEEDS_EXPLICIT_MAPPING')
            pages.append({'dimensions': [page.rect.width, page.rect.height],
                          'blocks': [{'bbox': list(block[:4]), 'text': block[4]}
                                     for block in page.get_text('blocks') if block[6] == 0]})
    markdown, mapping = render_document(source['sha256'], pages)
    manifest = {**recipe, 'source_version_ref': source['version_id'], 'work_id': source['work_id'],
                'dependencies': {source['path']: source['sha256'],
                                 source['preserved_blob']['path']: source['sha256'],
                                 'src/horisma_p0/document_reading.py': recipe['code_sha256']},
                'artifacts': {'document.md': sha(markdown.encode()), 'map.json': sha(encoded(mapping))},
                'page_count': len(pages), 'scientific_acceptance': False, 'release_authorized': False}
    folder = root/'outputs/document-readings'/sha(encoded(manifest))
    write_new(folder/'document.md', markdown.encode()); write_new(folder/'map.json', encoded(mapping))
    write_new(folder/'manifest.json', encoded(manifest))
    write_new(cache, encoded({'manifest': (folder/'manifest.json').relative_to(root).as_posix(), 'sha256': sha(encoded(manifest))}))
    return {**check_document(root, folder/'manifest.json'), 'manifest': str(folder/'manifest.json'), 'mode': 'BUILT_NATIVE_BASELINE', 'model_calls': 0}


def check_document(root, manifest_path):
    root, path = Path(root).resolve(), Path(manifest_path).resolve()
    if not path.is_relative_to(root/'outputs/document-readings'): raise ValueError('EXTERNAL_DOCUMENT_VIEW')
    raw = read(root, path.relative_to(root)); data = json.loads(raw)
    if path.parent.name != sha(raw): raise ValueError('DOCUMENT_MANIFEST_CHANGED')
    changed = [p for p, digest in data['dependencies'].items()
               if not (root/p).is_file() or sha(read(root, p)) != digest]
    for name, digest in data['artifacts'].items():
        if Path(name).name != name or sha((path.parent/name).read_bytes()) != digest:
            raise ValueError('DOCUMENT_ARTIFACT_CHANGED')
    return {'source_version_ref': data['source_version_ref'], 'page_count': data['page_count'],
            'preview_eligible': not changed, 'changed_dependencies': changed,
            'scientific_eligible': False, 'release_eligible': False}
