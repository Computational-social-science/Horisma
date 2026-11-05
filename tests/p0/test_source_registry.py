import json

import pymupdf
import pytest

from horisma_p0.source_registry import register_pdf, document_source


def test_additional_source_does_not_infer_dates_and_preserves_bytes(tmp_path):
    source = tmp_path/'1967-candidate.pdf'
    doc = pymupdf.open(); doc.new_page(); source.write_bytes(doc.tobytes()); doc.close()
    result = register_pdf(tmp_path, source)
    record = document_source(tmp_path, result['source_id'])
    assert record['historical_date_from_filename'] is None
    assert record['identity_status'].startswith('UNRESOLVED')
    assert (tmp_path/record['preserved_blob']['path']).read_bytes() == source.read_bytes()
    assert result == register_pdf(tmp_path, source)
    with pytest.raises(ValueError): document_source(tmp_path, 'local-../../unknown')
