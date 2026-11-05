"""Integrity checking for source-bound edge proposals; no semantic authentication."""
from .operators import digest, owned_path


def validate_edge(root, edge):
    if edge['kind'] not in {'REFERENCES_WORK', 'ACKNOWLEDGES_CONTRIBUTION_TO_WORK'}:
        raise ValueError('UNKNOWN_EDGE_KIND')
    if not isinstance(edge['target_work_id'], str) or not edge['target_work_id'].strip():
        raise ValueError('TARGET_WORK_REQUIRED')
    if len(edge['bindings']) < 2 or not {'source', 'target'} <= {x['side'] for x in edge['bindings']}:
        raise ValueError('SOURCE_AND_TARGET_BINDINGS_REQUIRED')
    for binding in edge['bindings']:
        raw = owned_path(root, binding['path']).read_bytes()
        if digest(raw) != binding['sha256']:
            raise ValueError('EDGE_DEPENDENCY_CHANGED')
    return {'edge_id': edge['edge_id'], 'integrity': 'BOUND',
            'semantic_status': 'PROPOSED_NOT_QUALIFIED',
            'reading_or_reliance_established': False, 'scientific_acceptance': False}
