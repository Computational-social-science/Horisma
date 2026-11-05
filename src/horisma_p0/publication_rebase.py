"""Narrow, byte-proven naming migration; no PDF parsing or inference."""
import copy
import json
from pathlib import Path

import yaml

from .research_slice import CONFIG, MAP, CHAPTER, check_slice, encoded, read, sha, write_new

HEAD = 'ops/state/publication-rebase-head.json'
CODE = 'src/horisma_p0/publication_rebase.py'
CHANGED = {CONFIG, MAP, CHAPTER, 'src/horisma_p0/book_gate.py'}


def scientific_projection(payload):
    result = copy.deepcopy(payload)
    result.pop('dependencies')
    for key in ['version', 'series_title', 'book_title', 'subtitle']:
        result['config'].pop(key, None)
    result['chapter'].pop('text_sha256')
    return result


def reconstruct(text, expected):
    # Historical Windows files may have used either newline representation.
    for candidate in [text.replace('\r\n', '\n'), text.replace('\r\n', '\n').replace('\n', '\r\n')]:
        if sha(candidate.encode()) == expected:
            return candidate.encode()
    raise ValueError('NON_NAMING_INPUT_CHANGE')


def prove_naming_inputs(root, old):
    deps = old['dependencies']
    changed = {p for p, digest in deps.items() if sha(read(root, p)) != digest}
    if changed != CHANGED:
        raise ValueError('UNEXPECTED_REBASE_DEPENDENCIES')
    chapter = read(root, CHAPTER).decode().replace('\r\n', '\n')
    prior = chapter.replace('# The Secrets of Terms\n\n## The Matthew Effect', '# The Matthew Effect', 1)
    reconstruct(prior, deps[CHAPTER])
    config_text = read(root, CONFIG).decode().replace('\r\n', '\n')
    prior = config_text.replace('version: 0.3.0', 'version: 0.2.0', 1).replace(
        'series_title: The Secrets of Terms\nbook_title: The Secrets of Terms\nsubtitle: The Matthew Effect',
        'series_title: Credit Where Credit Is Due\nbook_title: The Matthew Effect', 1)
    reconstruct(prior, deps[CONFIG])
    gate = read(root, 'src/horisma_p0/book_gate.py').decode().replace('\r\n', '\n')
    prior = gate.replace("'series_title':'The Secrets of Terms','book_title':'The Secrets of Terms',\n            'subtitle':'The Matthew Effect',",
                         "'series_title':'Credit Where Credit Is Due','book_title':'The Matthew Effect',", 1)
    reconstruct(prior, deps['src/horisma_p0/book_gate.py'])
    mapping = json.loads(read(root, MAP))
    prior = copy.deepcopy(mapping)
    prior.update(series_title='Credit Where Credit Is Due', book_title='The Matthew Effect',
                 content_sha256=old['chapter']['text_sha256'])
    prior.pop('subtitle', None)
    candidates = [json.dumps(prior, ensure_ascii=a, indent=2, sort_keys=s)+ending
                  for a in [False, True] for s in [False, True] for ending in ['', '\n']]
    if not any(sha(t.encode()) == deps[MAP] or sha(t.replace('\n', '\r\n').encode()) == deps[MAP] for t in candidates):
        raise ValueError('NON_NAMING_MAP_CHANGE')
    from .book_gate import check_book
    check_book(root, chapter.replace('\r\n', '\n'), mapping, mode='preview')
    return mapping, yaml.safe_load(config_text)


def rebase_publication(root, old_path):
    root = Path(root).resolve(); old_path = Path(old_path).resolve()
    if not old_path.is_relative_to(root/'outputs/research-slices'):
        raise ValueError('EXTERNAL_REBASE_BASE')
    raw = read(root, old_path.relative_to(root)); old = json.loads(raw)
    if old_path.parent.name != sha(raw): raise ValueError('CORRUPT_REBASE_BASE')
    mapping, config = prove_naming_inputs(root, old)
    new = copy.deepcopy(old); new['config'] = config
    new['chapter']['text_sha256'] = mapping['content_sha256']
    new['dependencies'] = {p: sha(read(root, p)) for p in old['dependencies']}
    if scientific_projection(old) != scientific_projection(new):
        raise ValueError('SCIENTIFIC_REBASE_CHANGE')
    new_raw = encoded(new); folder = root/'outputs/research-slices'/sha(new_raw)
    write_new(folder/'slice.json', new_raw)
    if not check_slice(root, folder)['preview_eligible']: raise ValueError('REBASE_NOT_CURRENT')
    receipt = {'profile': 'EXACT_NAMING_REBASE_1', 'old_base': old_path.relative_to(root).as_posix(),
               'new_base': (folder/'slice.json').relative_to(root).as_posix(),
               'operator_sha256': sha(read(root, CODE)), 'projection_sha256': sha(encoded(scientific_projection(new))),
               'changed_inputs': sorted(CHANGED), 'model_calls': 0, 'pdf_parse_calls': 0,
               'scientific_acceptance': False, 'release_authorized': False}
    receipt_raw = encoded(receipt); receipt_path = root/'outputs/publication-rebases'/sha(receipt_raw)/'receipt.json'
    write_new(receipt_path, receipt_raw)
    write_head(root, HEAD, {'receipt': receipt_path.relative_to(root).as_posix(), 'sha256': sha(receipt_raw)})
    write_head(root, 'ops/state/research-slice-head.json', {'slice': folder.relative_to(root).as_posix(), 'sha256': sha(new_raw)})
    return receipt


def write_head(root, path, payload):
    write_atomic(root, path, encoded(payload))


def write_atomic(root, path, raw):
    import os
    import tempfile
    target = root/path; target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=target.parent, prefix='.rebase-')
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
    finally:
        Path(temp).unlink(missing_ok=True)


def effective_suite_base(root, suite):
    """Retain frozen suite identity; require a verified current naming bridge."""
    root = Path(root).resolve()
    head = json.loads(read(root, HEAD)); path = Path(head['receipt'])
    raw = read(root, path); receipt = json.loads(raw)
    if (not (root/path).resolve().is_relative_to(root/'outputs/publication-rebases')
            or sha(raw) != head['sha256'] or path.parent.name != sha(raw)
            or receipt['operator_sha256'] != sha(read(root, CODE))):
        raise ValueError('INVALID_REBASE_RECEIPT')
    old_path, new_path = receipt['old_base'], receipt['new_base']
    if str(Path(old_path).parent.as_posix()) != suite['base_slice_path']:
        raise ValueError('WRONG_REBASE_SUITE')
    old_raw, new_raw = read(root, old_path), read(root, new_path)
    if sha(old_raw) != Path(old_path).parent.name or sha(new_raw) != Path(new_path).parent.name:
        raise ValueError('CORRUPT_REBASE_SNAPSHOT')
    old, new = json.loads(old_raw), json.loads(new_raw)
    prove_naming_inputs(root, old)
    if (scientific_projection(old) != scientific_projection(new)
            or sha(encoded(scientific_projection(new))) != receipt['projection_sha256']
            or not check_slice(root, root/Path(new_path).parent)['preview_eligible']):
        raise ValueError('STALE_OR_CHANGED_REBASE')
    mapping, config = prove_naming_inputs(root, old)
    expected = copy.deepcopy(old)
    expected['config'] = config
    expected['chapter']['text_sha256'] = mapping['content_sha256']
    expected['dependencies'] = {p: sha(read(root, p)) for p in old['dependencies']}
    if expected != new:
        raise ValueError('REBASE_NOT_EXACT_DERIVATION')
    current = json.loads(read(root, 'ops/state/research-slice-head.json'))
    if current != {'slice': Path(new_path).parent.as_posix(), 'sha256': sha(new_raw)}:
        raise ValueError('REBASE_HEAD_MISMATCH')
    return Path(new_path).parent.as_posix()


def check_publication_chain(root, case_path):
    from .card_publication import render_views
    from .book_gate import development_export_metadata
    root = Path(root).resolve()
    cards_head = json.loads(read(root, 'ops/state/event-cards-head.json'))
    path = Path(cards_head['cards']).resolve()
    if not path.is_relative_to(root/'outputs/event-cards'): raise ValueError('EXTERNAL_CARD_HEAD')
    raw = read(root, path.relative_to(root)); cards = json.loads(raw)
    if sha(raw) != path.parent.name: raise ValueError('CHANGED_CARD_HEAD')
    relative_case = Path(case_path).resolve().relative_to(root).as_posix()
    if cards['dependencies'].get(relative_case) != sha(read(root, relative_case)):
        raise ValueError('CARD_CASE_HEAD_MISMATCH')
    if any(sha(read(root, p)) != digest for p, digest in cards['dependencies'].items()):
        raise ValueError('STALE_INTEGRATED_CARDS')
    publication = json.loads(read(root, 'ops/state/card-publication-head.json'))
    qmd = Path(publication['quarto_source']).resolve()
    if not qmd.is_relative_to(root/'outputs/card-publication'): raise ValueError('EXTERNAL_PUBLICATION_HEAD')
    manifest = json.loads(read(root, (qmd.parent/'manifest.json').relative_to(root)))
    recipe = {'cards_sha256': sha(raw), 'renderer_sha256': sha(read(root, 'src/horisma_p0/card_publication.py')),
              'publication_metadata': development_export_metadata('card-apparatus')}
    if manifest != {**recipe, 'scientific_acceptance': False, 'release_authorized': False} or qmd.parent.name != sha(encoded(recipe)):
        raise ValueError('STALE_PUBLICATION_MANIFEST')
    views = render_views(cards['cards'])
    for key, name, expected in [('quarto_source', 'cards.qmd', views[0].encode()),
                                ('logseq_source', 'logseq.md', views[1].encode()),
                                ('anchors', 'anchors.json', encoded(views[2]))]:
        if Path(publication[key]).resolve() != qmd.parent/name or read(root, (qmd.parent/name).relative_to(root)) != expected:
            raise ValueError('CHANGED_PUBLICATION_VIEW')
    return {'cards': path.relative_to(root).as_posix(), 'publication': qmd.relative_to(root).as_posix(),
            'card_count': len(cards['cards']), 'dependencies_current': True,
            'scientific_acceptance': False, 'release_authorized': False}


def load_entity_cache(root):
    head = json.loads(read(root, 'ops/state/entity-slice-head.json'))
    path = Path(head['dataset']); raw = read(root, path)
    if (not (root/path).resolve().is_relative_to(root/'outputs/entity-slices')
            or sha(raw) != head['sha256'] or path.parent.name != sha(raw)):
        raise ValueError('CHANGED_ENTITY_CACHE_HEAD')
    payload = json.loads(raw)
    if any(sha(read(root, p)) != digest for p, digest in payload['dependencies'].items()):
        raise ValueError('CHANGED_ENTITY_CACHE_DEPENDENCY')
    return payload


def original_crosscheck(root, path, expected):
    seen = set()
    def load(path, digest):
        raw = read(root, path)
        if sha(raw) != digest or Path(path).parent.name != sha(raw):
            raise ValueError('CHANGED_CROSSCHECK_ANCESTOR')
        return raw, json.loads(raw)
    raw, cross = load(path, expected)
    while 'replayed_from' in cross:
        if path in seen or len(seen) >= 16: raise ValueError('CYCLIC_CROSSCHECK_ANCESTRY')
        seen.add(path); ref = cross['replayed_from']
        parent_raw, parent = load(ref['path'], ref['sha256'])
        derived = {**parent, 'slice_id': cross['slice_id'], 'replayed_from': ref,
                   'publication_rebase': cross['publication_rebase']}
        if cross != derived: raise ValueError('CHANGED_CROSSCHECK_REPLAY')
        path, raw, cross = ref['path'], parent_raw, parent
    return path, raw, cross


def rebuild_integrated(root, old_path):
    """Rebuild candidate projections and rescore sealed outputs, never infer."""
    from .entity_workflow import build_entity_dataset
    from .fidelity_report import campaign_report
    from .attribution_case import build_case
    from .event_cards import build_event_cards
    from .card_publication import export_cards
    root = Path(root).resolve()
    old_dataset = load_entity_cache(root)
    receipt = rebase_publication(root, old_path)
    base = Path(receipt['new_base']).parent
    cross_paths = [p for p in old_dataset['dependencies'] if '/transcription-crosscheck/' in p and p.endswith('/report.json')]
    if len(cross_paths) > 1: raise ValueError('AMBIGUOUS_REBASE_CROSSCHECK')
    cross_path = None
    if cross_paths:
        initial_raw = read(root, cross_paths[0]); cross = json.loads(initial_raw)
        if cross['slice_id'] != Path(old_dataset['base_slice_path']).name:
            raise ValueError('WRONG_ANCESTOR_CROSSCHECK')
        origin, old_cross_raw, cross = original_crosscheck(root, cross_paths[0], old_dataset['dependencies'][cross_paths[0]])
        if cross['slice_id'] != Path(receipt['old_base']).parent.name:
            raise ValueError('WRONG_ORIGINAL_CROSSCHECK')
        cross.update(slice_id=base.name, replayed_from={'path': origin, 'sha256': sha(old_cross_raw)},
                     publication_rebase=sha(encoded(receipt)))
        raw = encoded(cross); cross_path = root/base/'transcription-crosscheck'/sha(raw)/'report.json'
        write_new(cross_path, raw)
    entity = build_entity_dataset(root, root/base, cross_path)
    entity_path = Path(entity['dataset']).relative_to(root).as_posix()
    fh = json.loads(read(root, 'ops/state/fidelity-campaign-head.json'))
    old_report = json.loads(read(root, fh['report']))
    replay = campaign_report(root, root/old_report['suite_manifest'])
    report_path = Path(replay['report']).relative_to(root).as_posix()
    write_head(root, 'ops/state/fidelity-campaign-head.json', {'base_slice_id': base.name,
               'suite_id': fh['suite_id'], 'report': report_path, 'sha256': sha(read(root, report_path))})
    intake_path = root/'data/intake/derived/matthew-attribution-case/intake.json'
    intake = json.loads(intake_path.read_bytes()); previous_base = intake['base_slice_ref']
    intake['base_slice_ref'] = base.as_posix()
    entity_keys = [p for p in intake['dependencies'] if p.startswith('outputs/entity-slices/') and p.endswith('/dataset.json')]
    for previous, current in [(previous_base+'/slice.json', receipt['new_base']), *[(p, entity_path) for p in entity_keys]]:
        intake['dependencies'].pop(previous)
        intake['dependencies'][current] = sha(read(root, current))
    intake_path.write_bytes(encoded(intake)); case = build_case(root, intake_path)
    old_cards_head = json.loads(read(root, 'ops/state/event-cards-head.json'))
    old_cards = json.loads(Path(old_cards_head['cards']).read_bytes())
    card_intakes = [root/p for p in old_cards['dependencies'] if p.startswith('data/intake/')
                   and p.endswith('.json') and 'cards' in json.loads(read(root, p))]
    if len(card_intakes) != 1: raise ValueError('AMBIGUOUS_CARD_INTAKE')
    cards = build_event_cards(root, case['case'], card_intakes[0])
    publication = export_cards(root, cards['cards'])
    write_head(root, 'ops/state/event-cards-head.json', cards)
    write_head(root, 'ops/state/card-publication-head.json', publication)
    config_path = root/'.eidos/project.yaml'
    if config_path.exists():
        config = yaml.safe_load(config_path.read_text(encoding='utf-8'))
        paths = set(config['validity_inputs']) | {CODE, 'src/horisma_p0/card_publication.py'}
        for name in ['research-slice', 'entity-slice', 'fidelity-campaign', 'attribution-case',
                     'event-cards', 'card-publication', 'publication-rebase']:
            relative = 'ops/state/'+name+'-head.json'; paths.add(relative)
            value = json.loads(read(root, relative))
            for key in ['slice', 'dataset', 'report', 'case', 'cards', 'receipt', 'quarto_source', 'logseq_source', 'anchors']:
                if key not in value or not isinstance(value[key], str): continue
                path = Path(value[key]); path = path if path.is_absolute() else root/path
                if key == 'slice': path = path/'slice.json'
                path = path.resolve(); relative = path.relative_to(root).as_posix(); paths.add(relative)
                if path.suffix == '.json': paths.update(json.loads(read(root, relative)).get('dependencies', {}))
        config['validity_inputs'] = sorted(paths)
        write_atomic(root, '.eidos/project.yaml', yaml.safe_dump(config, sort_keys=False, allow_unicode=True).encode())
    return {'rebase': receipt, 'entity': entity_path, 'report': report_path, 'case': case['case'],
            'publication': check_publication_chain(root, case['case']), 'model_calls': 0, 'pdf_parse_calls': 0}
