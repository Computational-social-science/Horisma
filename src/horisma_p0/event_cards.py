"""Source-grounded event propositions, not a new historical verification authority."""
import json
from pathlib import Path
import re

from .attribution_case import check_case
from .research_slice import encoded, read, sha, write_new
from .temporal import validate_event, date_interval


def event_card(spec, nodes, card_ids):
    event = validate_event(spec['event'])
    if event['event_type'] == 'SYSTEM_REVISION': raise ValueError('HISTORICAL_CARD_REQUIRED')
    refs = spec['evidence_node_refs']
    if not refs or any(ref not in nodes for ref in refs): raise ValueError('BOUND_EVENT_EVIDENCE_REQUIRED')
    if any(link['card_ref'] not in card_ids for link in spec['links']): raise ValueError('DANGLING_EVENT_LINK')
    timing = spec.get('time_of_day')
    if timing is not None:
        if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', timing['value']): raise ValueError('INVALID_LOCAL_TIME')
        if timing['scope'] not in {'SESSION_START', 'INDIVIDUAL_START_REPORTED'}: raise ValueError('TIME_SCOPE_REQUIRED')
        if event['event_type'] == 'SCHEDULED_PRESENTATION' and timing['scope'] != 'SESSION_START':
            raise ValueError('SESSION_TIME_IS_NOT_TALK_TIME')
    missing = sorted({ref for ident in refs for ref in nodes[ident].get('missing_dependency_refs', [])})
    source_versions, seen = set(), set()
    def collect(ident):
        if ident in seen: return
        seen.add(ident); node = nodes[ident]
        if node.get('source_version_ref'): source_versions.add(node['source_version_ref'])
        for ref in node.get('refs', []): collect(ref)
    for ident in refs: collect(ident)
    card = {**spec, 'card_type': 'EVENT', 'schema_version': '0.1.0', 'disclosure': 'PRIVATE',
            'source_version_refs': sorted(source_versions),
            'normalized_event': event, 'account_interval': date_interval(spec['account_date']),
            'evidence_revisions': {ref: nodes[ref]['revision'] for ref in refs},
            'missing_dependency_refs': missing, 'assessment': None, 'assessment_missing_reason': 'NOT_ASSESSED',
            'readiness': 'BLOCKED_SOURCE_DEPENDENCY' if missing else 'UNQUALIFIED_EVIDENCE',
            'individual_start_time': None, 'individual_time_missing_reason': 'NOT_ESTABLISHED',
            'scientific_acceptance': False, 'release_authorized': False}
    card['revision'] = sha(encoded(card))
    return card


def build_event_cards(root, case_path, intake_path):
    root = Path(root).resolve(); case_path, intake_path = Path(case_path).resolve(), Path(intake_path).resolve()
    if not check_case(root, case_path)['preview_eligible']: raise ValueError('STALE_EVENT_CASE')
    case_raw = read(root, case_path.relative_to(root)); case = json.loads(case_raw)
    intake_raw = read(root, intake_path.relative_to(root)); intake = json.loads(intake_raw)
    ids = [c['card_id'] for c in intake['cards']]
    if len(ids) != len(set(ids)): raise ValueError('DUPLICATE_EVENT_CARD_ID')
    nodes = {n['id']: n for n in case['nodes']}
    cards = [event_card(spec, nodes, ids) for spec in intake['cards']]
    dependencies = {**case['dependencies'], case_path.relative_to(root).as_posix(): sha(case_raw),
                    intake_path.relative_to(root).as_posix(): sha(intake_raw)}
    for name in ['event_cards.py', 'temporal.py']:
        key = 'src/horisma_p0/'+name; dependencies[key] = sha(read(root, key))
    for key in ['spec/extensions/event_cards.yaml', 'spec/extensions/research_cards.yaml']:
        dependencies[key] = sha(read(root, key))
    payload = {'profile': 'CANDIDATE_EVENT_CARDS_0_1', 'case_id': case['case_id'], 'cards': cards,
               'dependencies': dependencies, 'scientific_acceptance': False, 'release_authorized': False}
    raw = encoded(payload); folder = root/'outputs/event-cards'/sha(raw)
    write_new(folder/'cards.json', raw)
    prose = ['# Matthew Effect: evidence-event cards', '', 'Private working cards. Source reports, schedule and inference are distinct; no accepted historical findings.']
    for card in cards:
        date = card['event']['date']; display = date['value'] or 'Unknown / interval'
        prose += ['', '## '+card['title'], '', '**Event:** '+display+' · '+card['event']['event_type'],
                  '', card['proposition'], '', '**Evidence permits:** '+card['support_scope'],
                  '', '**Limits:** '+card['limitations'], '', '**Status:** '+card['readiness'],
                  '', '**Source units:** '+', '.join(card['evidence_node_refs'])]
    write_new(folder/'cards.md', ('\n'.join(prose)+'\n').encode())
    return {'cards': str(folder/'cards.json'), 'reading': str(folder/'cards.md'), 'count': len(cards),
            'scientific_acceptance': False, 'release_authorized': False}
