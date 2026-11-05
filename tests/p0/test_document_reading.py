from horisma_p0.document_reading import render_document
from pathlib import Path
import json
import pytest
from horisma_p0.research_slice import encoded, sha


def test_complete_pages_exact_offsets_and_errors_are_preserved():
    pages = [{'dimensions': [100, 200], 'blocks': [
        {'bbox': [1, 2, 50, 60], 'text': 'Harniet [19731]\nThese results is preliminary.'}]},
        {'dimensions': [100, 200], 'blocks': []}]
    text, mapping = render_document('source', pages)
    unit = mapping['units'][0]
    a, b = unit['markdown_unicode_span']
    assert text[a:b] == pages[0]['blocks'][0]['text']
    assert mapping['page_count'] == 2 and mapping['pages_without_native_text'] == [1]
    assert not mapping['scientific_acceptance']
    assert (text, mapping) == render_document('source', pages)


def test_native_document_cache_survives_unrelated_base_revision_and_rejects_tamper(tmp_path, monkeypatch):
    import pymupdf
    from horisma_p0 import document_reading as module
    monkeypatch.setattr(module, 'check_slice', lambda *_: {'preview_eligible': True})
    doc = pymupdf.open(); page = doc.new_page(); page.insert_text((72, 72), 'Synthetic historical source.')
    raw = doc.tobytes(); doc.close()
    for relative in ['source.pdf', 'blob']:
        (tmp_path/relative).write_bytes(raw)
    code = tmp_path/'src/horisma_p0/document_reading.py'; code.parent.mkdir(parents=True)
    code.write_bytes(Path(module.__file__).read_bytes())
    state = tmp_path/'ops/state'; state.mkdir(parents=True)
    base = tmp_path/'base'; base.mkdir()
    source = {'sha256': sha(raw), 'path': 'source.pdf', 'preserved_blob': {'path': 'blob'},
              'version_id': 'syn:work@v1', 'work_id': 'syn:work'}
    payload = {'sources': {'3': source}}
    for turn in [0, 1]:
        payload['unrelated_profile_revision'] = turn
        body = encoded(payload); (base/'slice.json').write_bytes(body)
        (state/'research-slice-head.json').write_bytes(encoded({'slice': 'base', 'sha256': sha(body)}))
        result = module.build_document(tmp_path, '3')
        assert result['preview_eligible']
        assert result['mode'] == ('BUILT_NATIVE_BASELINE' if turn == 0 else 'CACHE_REUSED')
    path = Path(result['manifest'])
    payload['sources']['4'] = {**source, 'work_id': 'syn:other', 'version_id': 'syn:other@v1'}
    body = encoded(payload); (base/'slice.json').write_bytes(body)
    (state/'research-slice-head.json').write_bytes(encoded({'slice': 'base', 'sha256': sha(body)}))
    other = module.build_document(tmp_path, '4')
    pointer = next(p for p in (state/'document-reading-cache').glob('*.json')
                   if json.loads(p.read_bytes())['manifest'] == path.relative_to(tmp_path).as_posix())
    old_pointer = pointer.read_bytes()
    pointer.write_bytes(encoded({'manifest': Path(other['manifest']).relative_to(tmp_path).as_posix(),
                                'sha256': sha(Path(other['manifest']).read_bytes())}))
    with pytest.raises(ValueError, match='CACHE_RECIPE_MISMATCH'):
        module.build_document(tmp_path, '3')
    pointer.write_bytes(old_pointer)
    (path.parent/'document.md').write_bytes(b'tampered')
    with pytest.raises(ValueError, match='ARTIFACT_CHANGED'):
        module.check_document(tmp_path, path)


def test_document_manifest_change_and_source_change_are_distinct(tmp_path):
    from horisma_p0.document_reading import check_document
    source = tmp_path/'source'; source.write_bytes(b'original')
    payload = {'dependencies': {'source': sha(b'original')}, 'artifacts': {}, 'page_count': 1,
               'source_version_ref': 'syn:work@v1'}
    raw = encoded(payload); path = tmp_path/'outputs/document-readings'/sha(raw)/'manifest.json'
    path.parent.mkdir(parents=True); path.write_bytes(raw)
    source.write_bytes(b'changed')
    assert not check_document(tmp_path, path)['preview_eligible']
    path.write_bytes(b'{}')
    with pytest.raises(ValueError, match='MANIFEST_CHANGED'): check_document(tmp_path, path)


def test_reading_probe_coverage_is_not_factual_support():
    from horisma_p0.document_reading import audit_reading_candidate
    result = audit_reading_candidate('A did not coin it.', 'A coined it.', ['not coin'])
    assert result['probes'][0]['retrieval_gap']
    assert not result['scientific_acceptance']
