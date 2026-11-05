import json
from pathlib import Path

import pytest

from horisma_p0.entity_mentions import annotate_mentions, script_codes

CORPUS = json.loads((Path(__file__).resolve().parents[2] / 'spec/examples/entity_mentions_challenge.json').read_bytes())


@pytest.mark.parametrize('case', CORPUS['cases'], ids=lambda case: case['id'])
def test_frozen_constructed_name_and_coreference_cases(case):
    text = case['text']
    scopes = None
    if 'speaker_person_refs' in case:
        scopes = [{'context_id': 'synthetic-speaker-scope', 'start': 0, 'end': len(text),
                   'speaker_person_refs': case['speaker_person_refs'], 'speaker_evidence_refs':['synthetic:speaker']}]
    result = annotate_mentions(text, CORPUS['forms'], scopes)
    if 'mentions' in case:
        actual = [[row['literal_text'], row['link_state'], row['candidate_entity_refs']] for row in result['mentions']]
        assert actual == case['mentions']
    if 'corefs' in case:
        actual = [[row['literal_text'], row['link_state'], row['candidate_person_refs']] for row in result['coreferences']]
        assert actual == case['corefs']
    if 'basis' in case:
        assert result['mentions'][0]['linking_basis'] == case['basis']
    for row in result['mentions'] + result['coreferences']:
        start, end = row['character_span']
        assert text[start:end] == row['literal_text']
        assert not row['identity_qualified'] and not row['transcription_accepted']
    assert not result['qualified_links_produced']


def test_scripts_and_invalid_scopes():
    assert script_codes('默顿') == ['Hani']
    assert script_codes('روبرت') == ['Arab']
    with pytest.raises(ValueError, match='CONTEXT_RANGES'):
        annotate_mentions('text', [], [{'context_id': 'x', 'start': -1, 'end': 2}])


def test_ambiguous_names_remain_in_pronoun_candidates():
    result=annotate_mentions('Alex Smith thanked Harriet Zuckerman. He replied.',CORPUS['forms'])
    assert result['coreferences'][0]['candidate_person_refs']==['P2','P4','P5']
    assert result['coreferences'][0]['link_state']=='AMBIGUOUS'
    result=annotate_mentions('Harriet Zuckerman thanked Robert. He replied.',CORPUS['forms'])
    assert result['coreferences'][0]['candidate_person_refs']==['P1','P2']
    assert result['coreferences'][0]['link_state']=='AMBIGUOUS'


def test_narrowed_name_forms_belong_to_the_retained_entities():
    result=annotate_mentions('Robert K. Merton wrote. Merton replied.',CORPUS['forms'])
    row=result['mentions'][-1]
    assert row['candidate_name_form_refs']==['f5']
    assert row['matched_name_form_refs']==['f10','f5']


def test_identity_namespaces_and_speaker_evidence_are_required():
    a=annotate_mentions('Harriet Zuckerman',CORPUS['forms'],namespace='source:A')
    b=annotate_mentions('Harriet Zuckerman',CORPUS['forms'],namespace='source:B')
    assert a['mentions'][0]['mention_id']!=b['mentions'][0]['mention_id']
    with pytest.raises(ValueError,match='SOURCE_BOUND_KNOWN_SPEAKER_REQUIRED'):
        annotate_mentions('I wrote.',CORPUS['forms'],[{'context_id':'bad','start':0,'end':8,'speaker_person_refs':['C1']}])


def test_outer_author_is_not_automatically_a_quoted_speaker():
    text='Robert K. Merton wrote: "I replied."'
    scopes=[{'context_id':'author','start':0,'end':len(text),'speaker_person_refs':['P1'],
             'speaker_evidence_refs':['synthetic:byline']}]
    assert annotate_mentions(text,CORPUS['forms'],scopes)['coreferences'][0]['link_state']=='ABSTAINED'


@pytest.mark.parametrize('opening,closing',[('\u2018','\u2019'),("'","'"),('\u00ab','\u00bb')])
def test_single_quoted_or_guillemet_speech_is_not_outer_coreference(opening,closing):
    text='Harriet Zuckerman wrote: '+opening+'She replied.'+closing
    assert annotate_mentions(text,CORPUS['forms'])['coreferences'][0]['link_state']=='ABSTAINED'


def test_expanded_hypotheses_have_no_overlapping_short_mentions():
    rows=annotate_mentions('Robert Merton wrote.',CORPUS['forms'])['mentions']
    assert len(rows)==1 and rows[0]['literal_text']=='Robert Merton'


def test_uncatalogued_capitalized_span_prevents_false_unique_pronoun():
    result=annotate_mentions('Harriet Zuckerman thanked John Doe. He replied.',CORPUS['forms'])
    assert result['coreferences'][0]['link_state']=='ABSTAINED'
    assert result['coreferences'][0]['unresolved_antecedent_spans'][0]['literal_text']=='John Doe'


@pytest.mark.parametrize('suffix',['\n','\r\n','  ','\n\n','\n\n\n'])
def test_source_trailing_whitespace_does_not_erase_context(suffix):
    text='Harriet Zuckerman wrote. She replied.'+suffix
    result=annotate_mentions(text,CORPUS['forms'])
    assert len(result['contexts'])==1
    assert result['coreferences'][0]['candidate_person_refs']==['P2']
    assert result['coreferences'][0]['link_state']=='CANDIDATE'
    for row in result['mentions']+result['coreferences']:
        assert row['context_refs']
