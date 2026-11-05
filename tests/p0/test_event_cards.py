import pytest

from horisma_p0.event_cards import event_card


def spec():
    date = {'precision':'DAY','value':'1967-08-31','earliest':None,'latest':None,'calendar':'GREGORIAN','missing_reason':None}
    return {'card_id':'syn:card','historical_event_ref':'syn:session','event':{
        'event_type':'SCHEDULED_PRESENTATION','date':date,'verification':'PROVISIONAL','basis':'Synthetic programme'},
        'account_date':date,'evidence_node_refs':['source'], 'links':[],
        'time_of_day':{'value':'15:30','scope':'SESSION_START'}}


def test_session_time_never_becomes_an_individual_talk_time():
    raw = spec(); card = event_card(raw, {'source':{'revision':'v1'}}, ['syn:card'])
    assert card['individual_start_time'] is None and card['assessment'] is None
    assert card['normalized_event']['interval']['earliest'] == '1967-08-31'
    raw['time_of_day']['scope'] = 'INDIVIDUAL_START_REPORTED'
    with pytest.raises(ValueError, match='SESSION_TIME'): event_card(raw, {'source':{'revision':'v1'}}, ['syn:card'])


def test_missing_source_and_changed_source_propagate_to_card_revision():
    before = event_card(spec(), {'source':{'revision':'v1','missing_dependency_refs':['primary']}}, ['syn:card'])
    after = event_card(spec(), {'source':{'revision':'v2'}}, ['syn:card'])
    assert before['readiness'] == 'BLOCKED_SOURCE_DEPENDENCY'
    assert before['revision'] != after['revision'] and not after['scientific_acceptance']
