"""Constructed scope controls, not historical transcription gold."""
import pytest

from horisma_p0.quote_scopes import quote_structure, compare_quote_structure


def test_nested_quotes_and_apostrophes_keep_exact_offsets():
    text = 'O’Neil wrote: ‘García said, “I did not coin it.”’'
    result = quote_structure(text)
    assert result['status'] == 'BALANCED_SYNTAX_ONLY'
    assert [q['depth'] for q in result['quotes']] == [1, 2]
    assert result['quotes'][1]['parent_id'] == result['quotes'][0]['quote_id']
    assert all(text[q['start']:q['end']] == q['literal_text'] for q in result['quotes'])
    assert result['scientific_acceptance'] is False


@pytest.mark.parametrize('text', ['“Incomplete', 'orphan ”', '‘wrong nesting ”’'])
def test_broken_delimiters_cannot_be_completed(text):
    assert quote_structure(text)['status'] == 'UNRESOLVED_DELIMITERS'


def test_straight_quotes_and_bracketed_editorial_insertions_are_separate():
    text = 'He wrote: "It is now [1973] evident to me."'
    result = quote_structure(text)
    assert len(result['quotes']) == 1
    assert result['editorial_markers'][0]['literal_text'] == '[1973]'
    assert result['quotes'][0]['speaker_ref'] is None


def test_balanced_ocr_can_still_lose_an_outer_quote():
    source = '‘A said, “I did not coin it.”’'
    observed = 'A said, "I did not coin it."'
    result = compare_quote_structure(source, observed)
    assert result['observed']['status'] == 'BALANCED_SYNTAX_ONLY'
    assert result['maximum_depth_changed'] and result['delimiter_sequence_changed']
    assert not result['fidelity_qualified']


def test_same_text_is_not_an_image_fidelity_credential():
    result = compare_quote_structure('“same”', '“same”')
    assert not result['delimiter_sequence_changed']
    assert not result['fidelity_qualified']


def test_empty_and_non_text_are_not_clean_quotation_contexts():
    assert quote_structure('')['status'] == 'NO_TEXT'
    with pytest.raises(ValueError):
        quote_structure(None)


def test_damaged_editorial_year_and_source_scoping_are_explicit():
    first = quote_structure('"It is now [19731 evident."', namespace='source-a')
    second = quote_structure('"It is now [19731 evident."', namespace='source-b')
    assert first['bracket_status'] == 'UNRESOLVED_BRACKETS'
    assert first['quotes'][0]['quote_id'] != second['quotes'][0]['quote_id']
