"""Separate inference cache from Markdown rendering; one full-PDF OCR per recipe."""
from datetime import datetime, timezone
import importlib.metadata
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

from .document_reading import render_document, check_document
from .fidelity_blocks import normalized_bbox
from .probe_artifacts import load_attempt, seal_attempt
from .research_slice import check_slice, encoded, read, sha, write_new


def page_route(native_chars, hidden_chars, image_fraction):
    if (type(native_chars) is not int or type(hidden_chars) is not int or
            not 0 <= hidden_chars <= native_chars or not 0 <= image_fraction <= 1):
        raise ValueError('INVALID_PAGE_SIGNALS')
    if hidden_chars and image_fraction >= .7: return 'SCAN_WITH_HIDDEN_TEXT'
    if image_fraction >= .8 and native_chars-hidden_chars < 200: return 'IMAGE_DOMINANT'
    if native_chars < 40: return 'UNDETERMINED_REQUIRE_OCR'
    return 'NATIVE_TEXT_CANDIDATE'


def document_signals(source):
    import pymupdf
    rows = []
    with pymupdf.open(stream=source, filetype='pdf') as doc:
        for index, page in enumerate(doc):
            traces = page.get_texttrace()
            # Both counts use the same text-trace representation, not mismatched extraction counts.
            chars = sum(len(span['chars']) for span in traces)
            hidden = sum(len(span['chars']) for span in traces if span['type'] == 3)
            fraction = max(((pymupdf.Rect(image['bbox']) & page.rect).get_area()/page.rect.get_area()
                            for image in page.get_image_info()), default=0)
            rows.append({'pdf_page_index': index, 'native_trace_characters': chars,
                         'hidden_characters': hidden, 'max_image_area_fraction': fraction,
                         'route': page_route(chars, hidden, fraction)})
    return rows


def structured_pages(raw, page_count):
    """Retain literal spans/furniture and quarantine bad locators instead of clipping."""
    expected = {str(i+1) for i in range(page_count)}
    if set(raw.get('pages', {})) != expected: raise ValueError('INCOMPLETE_DOCUMENT_PAGES')
    for page in raw['pages'].values():
        if any(type(page['size'].get(k)) not in (int, float) or not math.isfinite(page['size'][k])
               or page['size'][k] <= 0 for k in ['width', 'height']):
            raise ValueError('INVALID_DOCUMENT_PAGE_DIMENSIONS')
    pages = [{'dimensions': [raw['pages'][str(i+1)]['size'][k] for k in ['width', 'height']],
              'blocks': []} for i in range(page_count)]
    quarantine, provenance = [], []
    for item in raw.get('texts', []):
        text = item.get('text', '')
        if not isinstance(text, str): raise ValueError('DOCUMENT_TEXT_REQUIRED')
        if not item.get('prov'):
            quarantine.append({'item_ref': item['self_ref'], 'text': text, 'reason': 'UNLOCATED_TEXT'}); continue
        pending, intervals, item_error = [], [], None
        for prov in item['prov']:
            try:
                span = prov.get('charspan', [0, len(text)])
                if (len(span) != 2 or any(type(v) is not int for v in span)
                        or not 0 <= span[0] <= span[1] <= len(text)):
                    raise ValueError('INVALID_TEXT_SPAN')
                index = prov['page_no']-1
                if type(prov['page_no']) is not int or not 0 <= index < page_count:
                    raise ValueError('INVALID_TEXT_PAGE')
                size = raw['pages'][str(index+1)]['size']
                box = normalized_bbox({'bbox': prov['bbox'], 'page_size': size,
                    'coordinate_system': 'DOCLING_PDF_POINTS_WITH_DECLARED_ORIGIN'}, 1, 1)
                rect = [box[0]*size['width'], box[1]*size['height'], box[2]*size['width'], box[3]*size['height']]
                pending.append((index, {'text': text[span[0]:span[1]], 'bbox': rect},
                    {'pdf_page_index': index,
                    'item_ref': item['self_ref'], 'producer_charspan': span, 'label': item.get('label'),
                    'original_provenance': prov}))
                intervals.append(span)
            except (ValueError, KeyError, TypeError) as exc:
                item_error = str(exc)
        cursor = 0
        for a, b in sorted(intervals):
            if a < cursor or text[cursor:a].strip(): item_error = item_error or 'UNCOVERED_OR_OVERLAPPING_TEXT'
            cursor = b
        if text[cursor:].strip(): item_error = item_error or 'UNCOVERED_TEXT_TAIL'
        if item_error:
            quarantine.append({'item_ref': item.get('self_ref'), 'text': text, 'prov': item['prov'],
                               'reason': item_error})
            continue
        for index, block, location in pending:
            location['block_ordinal'] = len(pages[index]['blocks'])
            pages[index]['blocks'].append(block); provenance.append(location)
    return pages, provenance, quarantine


def append_unplaced(markdown, mapping, quarantine, source_sha256):
    """Whole unaligned items stay searchable once, without fabricated passage bounds."""
    mapping['unplaced_units'] = []
    if quarantine:
        markdown += '\n## Unplaced OCR items — not eligible for passage support\n\n'
    for item in quarantine:
        ident = 'unplaced:' + sha(encoded([source_sha256, item['item_ref']]))
        markdown += '<!-- '+ident+' -->\n'
        start = len(markdown); markdown += item['text']; end = len(markdown); markdown += '\n\n'
        mapping['unplaced_units'].append({'unit_id': ident, 'item_ref': item['item_ref'],
            'markdown_unicode_span': [start, end], 'revision': sha(item['text'].encode()),
            'pdf_page_index': None, 'bbox_pdf_points': None, 'reason': item['reason'],
            'original_provenance': item.get('prov'), 'passage_binding_eligible': False})
    mapping['markdown_sha256'] = sha(markdown.encode())
    return markdown, mapping


def infer_document(root, source, signals):
    root = Path(root).resolve(); directory = root/'outputs/full-document-ocr'
    model_raw = read(root, '.rebuild/fidelity-models/manifest.json')
    worker_raw = read(root, 'scripts/full_document_worker.py')
    adapter_raw = read(root, 'scripts/fidelity_backend_worker.py')
    recipe = {'source_sha256': source['sha256'], 'docling_version': importlib.metadata.version('docling'),
              'worker_sha256': sha(worker_raw), 'adapter_sha256': sha(adapter_raw),
              'model_manifest_sha256': sha(model_raw), 'seed': 20261105}
    key = sha(encoded(recipe))
    if (directory/(key+'.head.json')).exists():
        ident, files = load_attempt(directory, key)
        if json.loads(files['request.json'])['recipe'] != recipe: raise ValueError('OCR_CACHE_RECIPE_CHANGED')
        return ident, files, 'INFERENCE_CACHE_REUSED'
    if not 1 <= len(signals) <= 26: raise ValueError('DOCUMENT_PAGE_BUDGET')
    token = uuid.uuid4().hex; lock = root/'ops/state/research-model-screen.lock'
    lock.parent.mkdir(parents=True, exist_ok=True)
    lease = lock.open('x')
    try:
        lease.write(json.dumps({'owner_token': token, 'kind': 'FULL_DOCUMENT_OCR'})); lease.flush()
        output = directory/'runs'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        output.mkdir(parents=True)
        request = {**recipe, 'recipe': recipe, 'owner_token': token, 'page_count': len(signals)}
        write_new(output/'input.pdf', read(root, source['preserved_blob']['path']))
        for name, body in [('request.json', encoded(request)), ('worker-source.py', worker_raw),
                           ('adapter-source.py', adapter_raw), ('model-manifest.json', model_raw)]:
            write_new(output/name, body)
        env = {k: v for k, v in os.environ.items() if not any(word in k.upper() for word in ['TOKEN', 'API_KEY'])}
        env.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_HUB_DISABLE_TELEMETRY='1', PYTHONIOENCODING='utf-8')
        started = time.monotonic(); record = {'status': 'UNRUN', 'wall_budget_seconds': 180,
            'sdk_document_timeout_seconds': 90, 'retries': 0, 'recipe': recipe, 'scientific_acceptance': False}
        try:
            with (output/'stdout.txt').open('wb') as stdout, (output/'stderr.txt').open('wb') as stderr:
                result = subprocess.run([sys.executable, str(root/'scripts/full_document_worker.py'),
                    '--request', str(output/'request.json'), '--sha256', sha(encoded(request))],
                    cwd=root, env=env, stdout=stdout, stderr=stderr, timeout=180)
            record.update(status='PROCESS_COMPLETED' if result.returncode == 0 else 'FAILED', returncode=result.returncode)
        except subprocess.TimeoutExpired:
            record['status'] = 'TIMEOUT'
        record['elapsed_seconds'] = time.monotonic()-started
        write_new(output/'process.json', encoded(record))
        ident = seal_attempt(directory, key, {p.name: p.read_bytes() for p in output.iterdir() if p.is_file()})
        _, files = load_attempt(directory, key)
        return ident, files, 'INFERENCE_RAN'
    finally:
        lease.close()
        if lock.exists() and json.loads(lock.read_bytes()).get('owner_token') == token: lock.unlink()


def build_ocr_document(root, source_id):
    root = Path(root).resolve()
    from .source_registry import document_source
    source = document_source(root, source_id); source_raw = read(root, source['preserved_blob']['path'])
    if sha(source_raw) != source['sha256']: raise ValueError('DOCUMENT_SOURCE_CHANGED')
    signals = document_signals(source_raw)
    ident, files, mode = infer_document(root, source, signals)
    process = json.loads(files['process.json'])
    if process['status'] != 'PROCESS_COMPLETED' or 'result.json' not in files:
        return {'status': process['status'], 'attempt_id': ident, 'mode': mode,
                'preview_eligible': False, 'scientific_eligible': False}
    result = json.loads(files['result.json']); request = json.loads(files['request.json'])
    if (result['producer_status'] != 'success' or result['source_sha256'] != source['sha256']
            or sha(files['document.raw.json']) != result['raw_sha256']):
        raise ValueError('PARTIAL_OR_UNBOUND_DOCUMENT_OUTPUT')
    raw = json.loads(files['document.raw.json']); pages, provenance, quarantine = structured_pages(raw, len(signals))
    markdown, mapping = render_document(source['sha256'], pages, transcription='LOCAL_OCR_CANDIDATE')
    markdown, mapping = append_unplaced(markdown, mapping, quarantine, source['sha256'])
    mapping.update(producer_units=provenance, quarantined_units=quarantine,
        reading_order='DOCLING_TEXT_ITEM_ORDER_UNQUALIFIED',
        table_count=len(raw.get('tables', [])), picture_count=len(raw.get('pictures', [])),
        limitation='Text view; table structure and pictures remain in raw JSON and the PDF, not silently certified.')
    key = sha(encoded(request['recipe'])); attempt_folder = 'outputs/full-document-ocr/attempts/'+ident
    dependencies = {source['path']: source['sha256'], source['preserved_blob']['path']: source['sha256']}
    for name in files: dependencies[attempt_folder+'/'+name] = sha(files[name])
    dependencies['outputs/full-document-ocr/'+key+'.head.json'] = sha(read(root, 'outputs/full-document-ocr/'+key+'.head.json'))
    for name in ['src/horisma_p0/document_ocr.py', 'src/horisma_p0/document_reading.py', 'src/horisma_p0/fidelity_blocks.py']:
        dependencies[name] = sha(read(root, name))
    manifest = {'source_sha256': source['sha256'], 'source_version_ref': source['version_id'], 'work_id': source['work_id'],
        'backend': 'DOCLING_FULL_PDF_LOCAL_OCR', 'backend_version': request['docling_version'], 'attempt_id': ident,
        'dependencies': dependencies, 'page_signals': signals, 'page_count': len(pages),
        'quarantined_unit_count': len(quarantine), 'table_count': len(raw.get('tables', [])),
        'artifacts': {'document.md': sha(markdown.encode()), 'map.json': sha(encoded(mapping))},
        'scientific_acceptance': False, 'release_authorized': False}
    folder = root/'outputs/document-readings'/sha(encoded(manifest))
    for name, body in [('document.md', markdown.encode()), ('map.json', encoded(mapping)), ('manifest.json', encoded(manifest))]:
        write_new(folder/name, body)
    return {**check_document(root, folder/'manifest.json'), 'manifest': str(folder/'manifest.json'),
            'mode': mode, 'quarantined_units': len(quarantine), 'attempt_id': ident}
