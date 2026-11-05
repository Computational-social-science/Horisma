"""Admissible/blocked graph witnesses, without historical gold."""
import copy
import json
from pathlib import Path

import pytest

from horisma_p0.attribution_case import assemble_case, select_literal
from horisma_p0.research_slice import encoded, sha


def example():
    return {'case_id': 'syn:case', 'concept_family_ref': 'syn:family',
            'nodes': [
                {'id': 'syn:original', 'kind': 'WORK_VERSION', 'refs': [], 'role': 'AUTHORSHIP', 'object_ref': 'syn:paper'},
                {'id': 'syn:missing', 'kind': 'MISSING_SOURCE', 'refs': [], 'missing_reason': 'SOURCE_UNAVAILABLE'},
                {'id': 'syn:empirical', 'kind': 'CONTRIBUTION_ANCHOR', 'refs': ['syn:original'], 'role': 'EMPIRICAL_BASIS', 'object_ref': 'syn:paper'},
                {'id': 'syn:byline', 'kind': 'CREDIT_ANCHOR', 'refs': ['syn:original'], 'role': 'AUTHORSHIP', 'object_ref': 'syn:paper'},
                {'id': 'syn:ack', 'kind': 'CONTRIBUTION_ANCHOR', 'refs': ['syn:original', 'syn:missing'], 'role': 'AUTHORSHIP', 'object_ref': 'syn:paper'}],
            'comparisons': [
                {'id': 'syn:role-control', 'contribution_ref': 'syn:empirical', 'credit_ref': 'syn:byline', 'policy_ref': 'syn:policy', 'temporal_view': 'RETROSPECTIVE_RECONSTRUCTION'},
                {'id': 'syn:missing-control', 'contribution_ref': 'syn:ack', 'credit_ref': 'syn:byline', 'policy_ref': 'syn:policy', 'temporal_view': 'RETROSPECTIVE_RECONSTRUCTION'}],
            'argument_units': [{'id': 'syn:argument', 'refs': ['syn:missing-control'], 'reader_question': 'Which contribution?'}]}


def test_role_control_and_missing_primary_do_not_become_miscredit_verdicts():
    result = assemble_case(example())
    rows = result['comparisons']
    assert rows[0]['readiness'] == 'ROLE_NONCOMPARABLE'
    assert rows[1]['readiness'] == 'BLOCKED_SOURCE_DEPENDENCY'
    assert rows[1]['missing_dependency_refs'] == ['syn:missing']
    assert all(row['assessment'] is None for row in rows)
    assert not result['scientific_eligible']
    assert result['benchmark_tasks'][0]['gold_answer'] is None
    assert result['argument_units'][0]['release_authorized'] is False
    assert result == assemble_case(example())


def test_actual_missing_source_resolution_changes_all_dependent_revisions():
    original = example()
    revised = copy.deepcopy(original)
    revised['nodes'][1] = {'id': 'syn:missing', 'kind': 'WORK_VERSION', 'refs': [], 'source_version_ref': 'syn:source@v2'}
    before, after = assemble_case(original), assemble_case(revised)
    assert before['comparisons'][1]['revision'] != after['comparisons'][1]['revision']
    assert before['benchmark_tasks'][1]['revision'] != after['benchmark_tasks'][1]['revision']
    assert before['argument_units'][0]['revision'] != after['argument_units'][0]['revision']
    assert after['comparisons'][1]['readiness'] == 'BLOCKED_QUALIFICATION'


@pytest.mark.parametrize('fault', ['dangling', 'cycle', 'duplicate', 'bad-kind', 'invented-qualification', 'comparison', 'role-type'])
def test_invalid_graphs_are_rejected(fault):
    spec = example()
    if fault == 'dangling': spec['nodes'][0]['refs'] = ['unknown']
    if fault == 'cycle': spec['nodes'][0]['refs'] = ['syn:empirical']
    if fault == 'duplicate': spec['nodes'].append(spec['nodes'][0])
    if fault == 'bad-kind': spec['nodes'][0]['kind'] = 'PASS'
    if fault == 'invented-qualification': spec['nodes'][0]['scientific_acceptance'] = True
    if fault == 'comparison': spec['comparisons'][0]['contribution_ref'] = 'unknown'
    if fault == 'role-type': spec['nodes'][2]['role'] = []
    with pytest.raises(ValueError): assemble_case(spec)


def test_unique_literal_spans_are_round_trip_and_no_repair():
    text = 'Old text: "Harniet [19731] did not coin it."'
    span = select_literal(text, '"Harniet', 'coin it."')
    assert text[span['start']:span['end']] == span['literal_text']
    assert 'Harniet' in span['literal_text']
    with pytest.raises(ValueError): select_literal(text, 'Harriet', 'coin it."')
    with pytest.raises(ValueError): select_literal(text + text, '"Harniet', 'coin it."')


def test_real_file_dependency_changes_invalidate_all_projections(tmp_path):
    from horisma_p0.attribution_case import build_case, check_case
    source = tmp_path/'source.md'; source.write_text('Synthetic source, version1.', encoding='utf-8')
    source_code = Path(__file__).resolve().parents[2]/'src/horisma_p0'
    for name in ['attribution_case.py', 'quote_scopes.py']:
        target = tmp_path/'src/horisma_p0'/name; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((source_code/name).read_bytes())
    vocab = tmp_path/'spec/controlled_vocabularies.yaml'; vocab.parent.mkdir()
    vocab.write_text('vocabularies:\n  contribution_role:\n    codes: {AUTHORSHIP: author, EMPIRICAL_BASIS: empirical}\n')
    spec = {'dependencies': {'source.md': sha(source.read_bytes())}, 'case': example()}
    intake = tmp_path/'intake.json'; intake.write_bytes(encoded(spec))
    first = build_case(tmp_path, intake); second = build_case(tmp_path, intake)
    assert first['case'] == second['case']
    assert check_case(tmp_path, first['case'])['preview_eligible']
    source.write_text('Synthetic source, version2.', encoding='utf-8')
    result = check_case(tmp_path, first['case'])
    assert not result['preview_eligible']
    assert result['changed_dependencies'] == ['source.md']
    assert set(result['affected_projections']) == {'comparisons', 'scientist_contributions', 'benchmark', 'book_arguments'}
    with pytest.raises(ValueError, match='STALE_CASE_INPUT'): build_case(tmp_path, intake)


def test_empty_or_dangling_comparison_norm_is_not_valid_intake():
    spec = example(); spec['comparisons'][0]['policy_ref'] = ''
    with pytest.raises(ValueError, match='COMPARISON_NORM'): assemble_case(spec)
