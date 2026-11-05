"""Version-bound candidate graphs shared by attribution data, tasks and book notes."""
import json
import os
from pathlib import Path
import tempfile
import yaml

from .quote_scopes import quote_structure
from .research_slice import encoded, read, sha, write_new

KINDS = {'WORK_VERSION', 'MISSING_SOURCE', 'PASSAGE', 'SOURCE_REPORT', 'CONTRIBUTOR',
         'CONTRIBUTION_ANCHOR', 'CREDIT_ANCHOR', 'PROPOSED_MECHANISM'}


def select_literal(text, start_anchor, end_anchor):
    if not all(isinstance(x, str) and x for x in [text, start_anchor, end_anchor]):
        raise ValueError('NONEMPTY_LITERAL_ANCHORS_REQUIRED')
    if text.count(start_anchor) != 1:
        raise ValueError('UNIQUE_START_REQUIRED')
    start = text.index(start_anchor)
    tail = text[start+len(start_anchor):]
    if tail.count(end_anchor) != 1:
        raise ValueError('UNIQUE_END_REQUIRED')
    end = start+len(start_anchor)+tail.index(end_anchor)+len(end_anchor)
    return {'start': start, 'end': end, 'literal_text': text[start:end],
            'context_sha256': sha(text.encode()), 'span_sha256': sha(text[start:end].encode())}


def assemble_case(spec):
    """Integrity and conditional comparability only; no registered review producer yet."""
    nodes = spec['nodes']
    comparisons = spec['comparisons']
    arguments = spec['argument_units']
    ids = [item['id'] for item in nodes+comparisons+arguments]
    if any(not isinstance(i, str) or not i for i in ids) or len(ids) != len(set(ids)):
        raise ValueError('UNIQUE_CASE_IDS_REQUIRED')
    lookup = {node['id']: node for node in nodes}
    for node in nodes:
        if node['kind'] not in KINDS or node.get('scientific_acceptance') not in (None, False):
            raise ValueError('UNQUALIFIED_CANDIDATE_NODE_REQUIRED')
        if not isinstance(node['refs'], list) or any(ref not in lookup for ref in node['refs']):
            raise ValueError('DANGLING_NODE_REFERENCE')
        if node['kind'] in {'CONTRIBUTION_ANCHOR', 'CREDIT_ANCHOR'} and any(
                not isinstance(node.get(key), str) or not node[key] for key in ['role', 'object_ref']):
            raise ValueError('TYPED_ROLE_AND_OBJECT_REQUIRED')
    resolved, visiting = {}, set()

    def resolve(ident):
        if ident in visiting: raise ValueError('CYCLIC_EVIDENCE_DEPENDENCY')
        if ident in resolved: return resolved[ident]
        visiting.add(ident)
        node = dict(lookup[ident])
        dependencies = {ref: resolve(ref)['revision'] for ref in node['refs']}
        missing = {ident} if node['kind'] == 'MISSING_SOURCE' else set()
        for ref in node['refs']: missing.update(resolved[ref]['missing_dependency_refs'])
        node.update(dependency_revisions=dependencies, missing_dependency_refs=sorted(missing),
                    scientific_acceptance=False)
        if node.get('literal_text') is not None:
            node['quote_structure'] = quote_structure(node['literal_text'], namespace=ident)
        node['revision'] = sha(encoded(node))
        resolved[ident] = node
        visiting.remove(ident)
        return node

    for ident in lookup: resolve(ident)
    projected = []
    for item in comparisons:
        if any(item.get(key) not in resolved for key in ['contribution_ref', 'credit_ref']):
            raise ValueError('DANGLING_COMPARISON_REFERENCE')
        left, right = resolved[item['contribution_ref']], resolved[item['credit_ref']]
        if left['kind'] != 'CONTRIBUTION_ANCHOR' or right['kind'] != 'CREDIT_ANCHOR':
            raise ValueError('TYPED_ANCHORS_REQUIRED')
        if not all(isinstance(item.get(key), str) and item[key] for key in ['policy_ref', 'temporal_view']):
            raise ValueError('VERSIONED_COMPARISON_NORM_REQUIRED')
        same_role = left.get('role') is not None and left.get('role') == right.get('role')
        same_object = left.get('object_ref') is not None and left.get('object_ref') == right.get('object_ref')
        missing = sorted(set(left['missing_dependency_refs']+right['missing_dependency_refs']))
        readiness = 'ROLE_NONCOMPARABLE' if not same_role else 'OBJECT_NONCOMPARABLE' if not same_object else (
            'BLOCKED_SOURCE_DEPENDENCY' if missing else 'BLOCKED_QUALIFICATION')
        row = {**item, 'same_role': same_role, 'same_object': same_object, 'readiness': readiness,
               'dependency_revisions': {left['id']: left['revision'], right['id']: right['revision']},
               'missing_dependency_refs': missing, 'assessment': None, 'assessment_missing_reason': 'NOT_ASSESSED',
               'scientific_acceptance': False, 'intent_established': False, 'causal_effect_established': False}
        row['revision'] = sha(encoded(row)); projected.append(row)
    tasks = []
    for row in projected:
        task = {'id': row['id']+':task', 'comparison_ref': row['id'], 'comparison_revision': row['revision'],
                'concept_family_ref': spec['concept_family_ref'], 'split': 'DEVELOPMENT_ONLY',
                'question': row.get('reader_question', 'What does this role-scoped comparison permit?'),
                'gold_answer': None, 'score': None, 'assessment_missing_reason': 'NOT_ASSESSED'}
        task['revision'] = sha(encoded(task)); tasks.append(task)
    all_records = {**resolved, **{row['id']: row for row in projected}}
    book = []
    for item in arguments:
        if any(ref not in all_records for ref in item['refs']): raise ValueError('DANGLING_ARGUMENT_REFERENCE')
        row = {**item, 'dependency_revisions': {ref: all_records[ref]['revision'] for ref in item['refs']},
               'scientific_acceptance': False, 'release_authorized': False}
        row['revision'] = sha(encoded(row)); book.append(row)
    return {'version': '0.1.0', 'case_id': spec['case_id'], 'concept_family_ref': spec['concept_family_ref'],
            'profile': 'PARTIAL_CANDIDATE_CASE_GRAPH_NOT_ADJUDICATION',
            'nodes': list(resolved.values()), 'comparisons': projected,
            'benchmark_tasks': tasks, 'argument_units': book,
            'scientific_eligible': False, 'release_eligible': False}


def validate_argument_bindings(root, arguments, dependencies):
    """An edition-level digest does not establish a correct paragraph locator."""
    fields = {'edition_artifact', 'edition_sha256', 'paragraph_unicode_span',
              'paragraph_sha256', 'paragraph_offset_unit'}
    for argument in arguments:
        if not fields.intersection(argument):
            continue
        if not fields.issubset(argument):
            raise ValueError('INCOMPLETE_ARGUMENT_BINDING')
        artifact = argument['edition_artifact']
        if artifact not in dependencies:
            raise ValueError('UNBOUND_ARGUMENT_EDITION')
        raw = read(root, artifact)
        if sha(raw) != argument['edition_sha256'] or dependencies[artifact] != sha(raw):
            raise ValueError('STALE_ARGUMENT_EDITION')
        if argument['paragraph_offset_unit'] != 'UNICODE_CODE_POINTS_IN_EXACT_UTF8_LF_SOURCE':
            raise ValueError('UNKNOWN_ARGUMENT_OFFSET_UNIT')
        text = raw.decode('utf-8')
        if '\r' in text:
            raise ValueError('ARGUMENT_REQUIRES_LF_SOURCE')
        span = argument['paragraph_unicode_span']
        if (not isinstance(span, list) or len(span) != 2
                or any(type(x) is not int for x in span)
                or not 0 <= span[0] < span[1] <= len(text)):
            raise ValueError('INVALID_ARGUMENT_SPAN')
        if sha(text[span[0]:span[1]].encode()) != argument['paragraph_sha256']:
            raise ValueError('STALE_ARGUMENT_PARAGRAPH')


def build_case(root, intake_path):
    """Rebuild an explicit private intake. File bindings precede graph assembly."""
    root = Path(root).resolve(); intake_path = Path(intake_path).resolve()
    intake_raw = read(root, intake_path.relative_to(root)); intake = json.loads(intake_raw)
    dependencies = {intake_path.relative_to(root).as_posix(): sha(intake_raw)}
    for relative, digest in intake['dependencies'].items():
        if sha(read(root, relative)) != digest: raise ValueError('STALE_CASE_INPUT:'+relative)
        dependencies[relative] = digest
    from .document_reading import check_document
    for relative in intake.get('document_manifests', []):
        if relative not in dependencies: raise ValueError('UNBOUND_DOCUMENT_MANIFEST')
        if not check_document(root, root/relative)['preview_eligible']: raise ValueError('STALE_CASE_DOCUMENT')
        document = json.loads(read(root, relative))
        dependencies.update(document['dependencies'])
        for name, digest in document['artifacts'].items():
            dependencies[(Path(relative).parent/name).as_posix()] = digest
    spec = json.loads(encoded(intake['case']))
    validate_argument_bindings(root, spec['argument_units'], dependencies)
    vocab_path = 'spec/controlled_vocabularies.yaml'; vocab_raw = read(root, vocab_path)
    roles = yaml.safe_load(vocab_raw)['vocabularies']['contribution_role']['codes']
    dependencies[vocab_path] = sha(vocab_raw)
    for node in spec['nodes']:
        if node['kind'] in {'CONTRIBUTION_ANCHOR', 'CREDIT_ANCHOR'} and node.get('role') not in roles:
            raise ValueError('UNKNOWN_CONTROLLED_CONTRIBUTION_ROLE')
        if node['kind'] == 'PASSAGE':
            artifact = node['context_artifact']
            if artifact not in dependencies: raise ValueError('UNBOUND_PASSAGE_CONTEXT')
            text = read(root, artifact).decode('utf-8')
            if 'context_span' in node:
                lo, hi = node['context_span']
                if any(type(x) is not int for x in [lo, hi]) or not 0 <= lo < hi <= len(text):
                    raise ValueError('INVALID_DOCUMENT_CONTEXT_SPAN')
                text = text[lo:hi]
            node.update(select_literal(text, node['start_anchor'], node['end_anchor']))
    for name in ['attribution_case.py', 'quote_scopes.py']:
        relative = 'src/horisma_p0/'+name; dependencies[relative] = sha(read(root, relative))
    payload = assemble_case(spec)
    payload.update(dependencies=dependencies, base_slice_ref=intake.get('base_slice_ref'),
                   local_free=True, mandatory_human_review=False)
    raw = encoded(payload); folder = root/'outputs/attribution-cases'/sha(raw)
    write_new(folder/'case.json', raw)
    # Verify the complete input set once more before advertising this immutable result.
    if any(sha(read(root, p)) != digest for p, digest in dependencies.items()):
        raise ValueError('CASE_INPUT_CHANGED_DURING_BUILD')
    state = root/'ops/state/attribution-case-head.json'; state.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.case-', dir=state.parent)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(encoded({'case': (folder/'case.json').relative_to(root).as_posix(), 'sha256': sha(raw)}))
    os.replace(temporary, state)
    return {'case': str(folder/'case.json'), 'nodes': len(payload['nodes']),
            'comparisons': len(payload['comparisons']), 'benchmark_tasks': len(payload['benchmark_tasks']),
            'argument_units': len(payload['argument_units']), 'preview_eligible': True,
            'scientific_eligible': False, 'release_eligible': False}


def check_case(root, path):
    root, path = Path(root).resolve(), Path(path).resolve()
    if not path.is_relative_to(root/'outputs/attribution-cases'): raise ValueError('EXTERNAL_CASE')
    raw = read(root, path.relative_to(root)); payload = json.loads(raw)
    if sha(raw) != path.parent.name: raise ValueError('CASE_DIGEST_CHANGED')
    changed = [p for p, digest in payload['dependencies'].items()
               if not (root/p).is_file() or sha(read(root, p)) != digest]
    return {'case_id': payload['case_id'], 'preview_eligible': not changed,
            'base_slice_ref': payload.get('base_slice_ref'),
            'changed_dependencies': changed, 'scientific_eligible': False, 'release_eligible': False,
            'affected_projections': ['comparisons', 'scientist_contributions', 'benchmark', 'book_arguments'] if changed else []}
