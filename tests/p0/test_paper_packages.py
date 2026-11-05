import json

import pytest

from horisma_p0.paper_packages import cached_package, locate_packaged_unit
from horisma_p0.probe_artifacts import seal_attempt
from horisma_p0.research_slice import encoded, sha


def test_cached_package_cannot_promote_a_tampered_summary(tmp_path):
    output = tmp_path/'package'; paper = output/'reading/references/paper.md'
    paper.parent.mkdir(parents=True); paper.write_text('Synthetic reading.')
    summary = {'package': str(output/'reading'), 'map': str(tmp_path/'map.json'),
               'source_version_ref': 'synthetic@1', 'scientific_acceptance': False, 'release_authorized': False}
    record = {'recipe': {'key': 'recipe'}, 'files': {paper.relative_to(tmp_path).as_posix(): sha(paper.read_bytes())}, 'summary': summary}
    final = output/'package.json'; final.write_bytes(encoded(record))
    seal_attempt(output, 'package', {'package.json': final.read_bytes()})
    result = cached_package(tmp_path, output, record['recipe'], 'synthetic@1', tmp_path/'map.json')
    assert result['scientific_acceptance'] is False
    with pytest.raises(ValueError, match='RECIPE'): cached_package(tmp_path, output, {'key': 'other'}, 'synthetic@1', tmp_path/'map.json')
    (paper.parent/'extra.md').write_text('Unknown file.')
    with pytest.raises(ValueError, match='INVENTORY'): cached_package(tmp_path, output, record['recipe'], 'synthetic@1', tmp_path/'map.json')
    (paper.parent/'extra.md').unlink()
    record['summary']['scientific_acceptance'] = True; final.write_bytes(encoded(record))
    with pytest.raises(ValueError, match='MANIFEST'): cached_package(tmp_path, output, record['recipe'], 'synthetic@1', tmp_path/'map.json')


def test_unit_alignment_is_marker_scoped_and_only_boundary_whitespace_can_change():
    text = '<!-- first -->\nDid not coin.\n<!-- next -->\nDid coin.\n'
    aligned = locate_packaged_unit(text, 'Did not coin.  \n', 'first')
    assert text[slice(*aligned['span'])] == 'Did not coin.'
    assert aligned['transformation'] == 'BOUNDARY_WHITESPACE_ONLY'
    with pytest.raises(ValueError, match='TEXT_MISSING'): locate_packaged_unit(text, 'Did coin.', 'first')
