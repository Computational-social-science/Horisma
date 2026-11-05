"""Fixed role-scoped triage; input coding requires its own evidence receipts."""
ROLES = {'DISPLAYED_BYLINE', 'CONCEPT_DEVELOPMENT', 'MATERIAL_CONTRIBUTION',
         'LABEL_NAMING', 'UNKNOWN'}


def credit_triage(*, role, contributor_named, explicitly_exclusive, context_complete,
                  acknowledgment_comparable):
    if role not in ROLES or any(type(x) is not bool for x in
            [contributor_named, explicitly_exclusive, context_complete, acknowledgment_comparable]):
        raise ValueError('INVALID_ROLE_OR_TYPED_FLAGS')
    if role == 'DISPLAYED_BYLINE':
        result = 'BYLINE_DESCRIPTION_NOT_CONTRIBUTION_OMISSION'
    elif role == 'UNKNOWN' or not context_complete:
        result = 'CONTEXT_EXPANSION_REQUIRED'
    elif role == 'LABEL_NAMING':
        result = 'NAMING_EVIDENCE_REQUIRED'
    elif contributor_named:
        result = 'CONTRIBUTOR_MENTIONED_ROLE_QUALITY_UNRESOLVED'
    elif not acknowledgment_comparable:
        result = 'ROLE_COMPARABLE_EVIDENCE_REQUIRED'
    elif explicitly_exclusive:
        result = 'POTENTIAL_EXCLUSIVE_CREDIT_CONFLICT'
    else:
        result = 'POTENTIAL_CONTRIBUTION_COVERAGE_GAP'
    return {'triage': result, 'scientific_assessment': None,
            'intent_established': False, 'causal_effect_established': False}
