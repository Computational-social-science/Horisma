"""Conservative lexical role proposals and scope coverage diagnostics."""
import re


def role_proposal(text):
    t = re.sub(r'\s+', ' ', text).lower()
    cues = {
        'DISPLAYED_BYLINE': r'\b(byline|listed author|appeared under .*name)\b',
        'LABEL_NAMING': r'\b(coined|coinage|named the term)\b',
        'CONCEPT_DEVELOPMENT': r'\b(developed the concept|conceptual development)\b',
        'MATERIAL_CONTRIBUTION': r'\b(interview materials|interviews|joint authorship)\b',
    }
    found = [role for role, pattern in cues.items() if re.search(pattern, t)]
    return {'roles': found, 'role': found[0] if len(found) == 1 else 'UNKNOWN',
            'status': 'LEXICAL_PROPOSAL' if len(found) == 1 else 'ABSTAINED',
            'negation_or_reporting_resolved': False, 'qualified_semantic_coding': False}


def context_coverage(*, supplied_scope, required_scope, truncated, unresolved_reference):
    scopes = {'WINDOW', 'PARAGRAPH', 'DOCUMENT'}
    if supplied_scope not in scopes or required_scope not in scopes or any(type(x) is not bool for x in [truncated, unresolved_reference]):
        raise ValueError('INVALID_CONTEXT_INPUT')
    rank = {'WINDOW': 0, 'PARAGRAPH': 1, 'DOCUMENT': 2}
    complete = rank[supplied_scope] >= rank[required_scope] and not truncated and not unresolved_reference
    return {'coverage_sufficient': complete, 'semantic_completeness_qualified': False,
            'status': 'COVERAGE_ONLY' if complete else 'CONTEXT_EXPANSION_REQUIRED'}
