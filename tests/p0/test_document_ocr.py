import pytest
import json
import subprocess

from horisma_p0.document_ocr import page_route, structured_pages, append_unplaced


def test_hidden_text_does_not_disable_ocr_and_visible_digital_text_is_distinct():
    assert page_route(6000, 5000, 1) == 'SCAN_WITH_HIDDEN_TEXT'
    assert page_route(190, 0, 1) == 'IMAGE_DOMINANT'
    assert page_route(6000, 0, .1) == 'NATIVE_TEXT_CANDIDATE'
    with pytest.raises(ValueError): page_route(1, 2, .5)


def test_footnotes_exact_spans_and_page_coverage_are_retained():
    raw = {'pages': {'1': {'size': {'width': 100, 'height': 200}}}, 'texts': [
        {'self_ref': '#/texts/0', 'text': '[1973]', 'label': 'footnote',
         'prov': [{'page_no': 1, 'charspan': [0, 6],
                   'bbox': {'l': 0, 'r': 90, 't': 50, 'b': 20, 'coord_origin': 'BOTTOMLEFT'}}]}]}
    pages, provenance, quarantine = structured_pages(raw, 1)
    assert pages[0]['blocks'][0]['text'] == '[1973]'
    assert provenance[0]['label'] == 'footnote' and not quarantine
    raw['texts'][0]['prov'][0]['charspan'] = [0, 999]
    pages, _, quarantine = structured_pages(raw, 1)
    assert not pages[0]['blocks'] and quarantine[0]['text'] == '[1973]'
    with pytest.raises(ValueError, match='INCOMPLETE_DOCUMENT'): structured_pages(raw, 2)


@pytest.mark.parametrize('size', [0, -1, float('nan'), float('inf')])
def test_invalid_page_dimensions_are_rejected(size):
    with pytest.raises(ValueError, match='PAGE_DIMENSIONS'):
        structured_pages({'pages': {'1': {'size': {'width': size, 'height': 100}}}}, 1)


def test_partial_valid_spans_do_not_duplicate_an_unaligned_item():
    box = {'l': 0, 'r': 90, 't': 50, 'b': 20, 'coord_origin': 'BOTTOMLEFT'}
    raw = {'pages': {'1': {'size': {'width': 100, 'height': 200}}}, 'texts': [
        {'self_ref': '#/texts/0', 'text': 'Never duplicate this whole item.',
         'prov': [{'page_no': 1, 'charspan': [0, 5], 'bbox': box},
                  {'page_no': 1, 'charspan': [6, 999], 'bbox': box}]}]}
    pages, _, quarantine = structured_pages(raw, 1)
    assert not pages[0]['blocks'] and len(quarantine) == 1
    text, mapping = append_unplaced('header\n', {}, quarantine, 'source')
    assert text.count(raw['texts'][0]['text']) == 1
    unit = mapping['unplaced_units'][0]
    assert text[slice(*unit['markdown_unicode_span'])] == raw['texts'][0]['text']
    assert unit['pdf_page_index'] is None and not unit['passage_binding_eligible']


def test_timeout_is_sealed_reused_and_foreign_lease_not_removed(tmp_path, monkeypatch):
    from horisma_p0 import document_ocr as module
    for path in ['.rebuild/fidelity-models/manifest.json', 'scripts/full_document_worker.py', 'scripts/fidelity_backend_worker.py', 'source.pdf']:
        target = tmp_path/path; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(b'{}')
    monkeypatch.setattr(module.importlib.metadata, 'version', lambda _: 'fixture')
    calls = []
    def timeout(*args, **kwargs):
        calls.append(True); raise subprocess.TimeoutExpired(args[0], 180)
    monkeypatch.setattr(module.subprocess, 'run', timeout)
    source = {'sha256': 'fixture', 'preserved_blob': {'path': 'source.pdf'}}
    ident, files, mode = module.infer_document(tmp_path, source, [{}])
    assert json.loads(files['process.json'])['status'] == 'TIMEOUT'
    again = module.infer_document(tmp_path, source, [{}])
    assert again[0] == ident and again[2] == 'INFERENCE_CACHE_REUSED' and len(calls) == 1
    lock = tmp_path/'ops/state/research-model-screen.lock'; lock.write_text('foreign')
    source['sha256'] = 'other-input'
    with pytest.raises(FileExistsError): module.infer_document(tmp_path, source, [{}])
    assert lock.read_text() == 'foreign'
