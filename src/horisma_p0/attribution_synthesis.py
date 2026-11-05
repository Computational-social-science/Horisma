"""Typed inference proposals: credit synthesis without silently upgrading evidence."""
from datetime import date

EVENTS = {'PRINTED_USAGE', 'SCHEDULED_PRESENTATION', 'REPORTED_DELIVERY',
          'PUBLICATION', 'RETROSPECTIVE_ACKNOWLEDGMENT', 'COINAGE'}


def chronology_constraint(evidence, target):
    """Compare closed, explicitly bounded dates for a supplied same-sense context."""
    for event in (evidence, target):
        if not isinstance(event['concept_sense_id'], str) or not event['concept_sense_id'].strip():
            raise ValueError('EXPLICIT_CONCEPT_SENSE_REQUIRED')
        if event['kind'] not in EVENTS:
            raise ValueError('UNKNOWN_EVENT_KIND')
        lo, hi = date.fromisoformat(event['earliest']), date.fromisoformat(event['latest'])
        if lo > hi:
            raise ValueError('REVERSED_DATE_INTERVAL')
    comparable = evidence['concept_sense_id'] == target['concept_sense_id']
    prior = date.fromisoformat(evidence['latest']) < date.fromisoformat(target['earliest'])
    reasons = []
    if comparable and evidence['kind'] == 'PRINTED_USAGE' and target['kind'] == 'COINAGE' and prior:
        reasons.append('EARLIER_USAGE_CHALLENGES_LATER_FIRST_COINAGE')
    if evidence['kind'] == 'SCHEDULED_PRESENTATION' and target['kind'] in {'REPORTED_DELIVERY', 'COINAGE'}:
        reasons.append('SCHEDULE_DOES_NOT_ESTABLISH_DELIVERY_OR_COINAGE')
    if evidence['kind'] == 'PUBLICATION' and target['kind'] == 'COINAGE':
        reasons.append('PUBLICATION_DATE_DOES_NOT_ESTABLISH_COINAGE')
    return {'comparable_context': comparable, 'flags': reasons,
            'status': 'INFERENCE_CONSTRAINT_ONLY', 'scientific_acceptance': False}


def synthesize_contribution(acknowledgment):
    """Preserve the target work, actors, original wording and retrospective scope."""
    required = {'evidence_id', 'work_id', 'speaker', 'contributor', 'source_sha256',
                'locator', 'assertion', 'material_basis', 'qualified_evidence'}
    if set(acknowledgment) != required:
        raise ValueError('EXPLICIT_ACKNOWLEDGMENT_FIELDS_REQUIRED')
    if acknowledgment['assertion'] != 'SHOULD_HAVE_BEEN_JOINT_AUTHORSHIP':
        raise ValueError('UNSUPPORTED_ACKNOWLEDGMENT_TYPE')
    if type(acknowledgment['qualified_evidence']) is not bool:
        raise ValueError('EXPLICIT_QUALIFICATION_REQUIRED')
    for key in required - {'qualified_evidence'}:
        if not isinstance(acknowledgment[key], str) or not acknowledgment[key].strip():
            raise ValueError('NONEMPTY_EVIDENCE_BINDINGS_REQUIRED')
    return {'basis': acknowledgment,
            'direct_proposals': ['RETROSPECTIVE_JOINT_AUTHORSHIP_ENTITLEMENT',
                                 'ACKNOWLEDGED_MATERIAL_DEPENDENCE'],
            'derived_proposals': ['CONCEPT_CONTRIBUTION_REQUIRES_ROLE_SPECIFIC_SYNTHESIS',
                                  'SOLE_BYLINE_IS_INCOMPLETE_CONTRIBUTION_PROXY'],
            'unresolved': ['SOLE_OR_JOINT_LABEL_NAMING', 'EXACT_COINAGE_DATE',
                           'BYLINE_CAUSED_LATER_MISCREDIT', 'POPULATION_MISCREDIT_PREVALENCE'],
            'hypothesis': 'SINGLE_BYLINE_MAY_MEDIATE_LATER_CREDIT_OMISSION',
            'scientific_acceptance': False, 'causal_effect_established': False}
