import copy
import json
from pathlib import Path

import pytest

from horisma_p0 import publication_rebase as module
from horisma_p0.research_slice import encoded, sha


def fixture(root, monkeypatch):
    monkeypatch.setattr(module, 'check_slice', lambda *args: {'preview_eligible': True})
    old_inputs = {
        module.CHAPTER: '# The Matthew Effect\n',
        module.CONFIG: 'version: 0.2.0\nseries_title: Credit Where Credit Is Due\nbook_title: The Matthew Effect\n',
        'src/horisma_p0/book_gate.py': "{'series_title':'Credit Where Credit Is Due','book_title':'The Matthew Effect',\n}",
        'source': 'Unchanged synthetic source',
    }
    old_map = {'content_sha256': sha(old_inputs[module.CHAPTER].encode()), 'paragraphs': [], 'sources': {},
               'series_title': 'Credit Where Credit Is Due', 'book_title': 'The Matthew Effect'}
    old_inputs[module.MAP] = json.dumps(old_map, indent=2, sort_keys=True)
    old = {'config': {'version':'0.2.0','series_title':'Credit Where Credit Is Due','book_title':'The Matthew Effect'},
           'chapter': {'text_sha256':old_map['content_sha256'], 'paragraphs': []},
           'dependencies': {p:sha(t.encode()) for p,t in old_inputs.items()}, 'sources': {}, 'regions': {}}
    for p,t in old_inputs.items():
        path=root/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(t.encode())
    (root/module.CHAPTER).write_text('# The Secrets of Terms\n\n## The Matthew Effect\n',encoding='utf-8',newline='\n')
    (root/module.CONFIG).write_text('version: 0.3.0\nseries_title: The Secrets of Terms\nbook_title: The Secrets of Terms\nsubtitle: The Matthew Effect\n',encoding='utf-8',newline='\n')
    (root/'src/horisma_p0/book_gate.py').write_text("{'series_title':'The Secrets of Terms','book_title':'The Secrets of Terms',\n            'subtitle':'The Matthew Effect',\n}",encoding='utf-8',newline='\n')
    current=copy.deepcopy(old_map);current.update(series_title='The Secrets of Terms',book_title='The Secrets of Terms',subtitle='The Matthew Effect',content_sha256=sha((root/module.CHAPTER).read_bytes()))
    (root/module.MAP).write_bytes(encoded(current))
    code=root/module.CODE;code.write_bytes(Path(module.__file__).read_bytes())
    raw=encoded(old);path=root/'outputs/research-slices'/sha(raw)/'slice.json';path.parent.mkdir(parents=True);path.write_bytes(raw)
    return path


@pytest.mark.parametrize('changed', [None, module.CHAPTER, module.CONFIG, module.MAP, 'src/horisma_p0/book_gate.py', 'source'])
def test_only_exact_naming_changes_can_reuse_frozen_inputs(tmp_path,monkeypatch,changed):
    old=fixture(tmp_path,monkeypatch)
    if changed:
        with (tmp_path/changed).open('ab') as stream:stream.write(b'\nChanged scientific input')
        with pytest.raises(ValueError):module.rebase_publication(tmp_path,old)
    else:
        receipt=module.rebase_publication(tmp_path,old)
        assert receipt['model_calls']==receipt['pdf_parse_calls']==0
        suite={'base_slice_path':old.parent.relative_to(tmp_path).as_posix()}
        assert module.effective_suite_base(tmp_path,suite)==str(Path(receipt['new_base']).parent.as_posix())
        assert module.rebase_publication(tmp_path,old)==receipt


@pytest.mark.parametrize('fault', ['receipt','head','wrong-suite','new-payload'])
def test_rebase_chain_tampering_fails_closed(tmp_path,monkeypatch,fault):
    old=fixture(tmp_path,monkeypatch);receipt=module.rebase_publication(tmp_path,old)
    suite={'base_slice_path':old.parent.relative_to(tmp_path).as_posix()}
    head=json.loads((tmp_path/module.HEAD).read_bytes())
    if fault=='receipt':(tmp_path/head['receipt']).write_bytes(b'{}')
    if fault=='head':(tmp_path/'ops/state/research-slice-head.json').write_bytes(b'{}')
    if fault=='wrong-suite':suite['base_slice_path']='outputs/research-slices/wrong'
    if fault=='new-payload':(tmp_path/receipt['new_base']).write_bytes(b'{}')
    with pytest.raises(ValueError):module.effective_suite_base(tmp_path,suite)


def test_rehashed_new_snapshot_cannot_forge_its_metadata(tmp_path,monkeypatch):
    old=fixture(tmp_path,monkeypatch);receipt=module.rebase_publication(tmp_path,old)
    value=json.loads((tmp_path/receipt['new_base']).read_bytes())
    value['config']['subtitle']='Invented subtitle'
    raw=encoded(value);new=tmp_path/'outputs/research-slices'/sha(raw)/'slice.json'
    new.parent.mkdir();new.write_bytes(raw)
    head=json.loads((tmp_path/module.HEAD).read_bytes());record=json.loads((tmp_path/head['receipt']).read_bytes())
    record['new_base']=new.relative_to(tmp_path).as_posix()
    body=encoded(record);path=tmp_path/'outputs/publication-rebases'/sha(body)/'receipt.json';path.parent.mkdir();path.write_bytes(body)
    module.write_head(tmp_path,module.HEAD,{'receipt':path.relative_to(tmp_path).as_posix(),'sha256':sha(body)})
    module.write_head(tmp_path,'ops/state/research-slice-head.json',{'slice':new.parent.relative_to(tmp_path).as_posix(),'sha256':sha(raw)})
    with pytest.raises(ValueError,match='EXACT_DERIVATION'):
        module.effective_suite_base(tmp_path,{'base_slice_path':old.parent.relative_to(tmp_path).as_posix()})


def test_card_view_tampering_is_checked_by_integrated_entry(tmp_path):
    from horisma_p0.card_publication import export_cards
    from test_card_publication import card
    renderer=tmp_path/'src/horisma_p0/card_publication.py';renderer.parent.mkdir(parents=True)
    import horisma_p0.card_publication as publication_module
    renderer.write_bytes(Path(publication_module.__file__).read_bytes())
    case=tmp_path/'case.json';case.write_bytes(b'{}')
    payload={'dependencies':{'case.json':sha(b'{}')},'cards':[card('syn:a')]}
    raw=encoded(payload);path=tmp_path/'outputs/event-cards'/sha(raw)/'cards.json';path.parent.mkdir(parents=True);path.write_bytes(raw)
    module.write_head(tmp_path,'ops/state/event-cards-head.json',{'cards':str(path)})
    publication=export_cards(tmp_path,path)
    module.write_head(tmp_path,'ops/state/card-publication-head.json',publication)
    assert module.check_publication_chain(tmp_path,case)['dependencies_current']
    Path(publication['quarto_source']).write_text('Wrong book text',encoding='utf-8')
    with pytest.raises(ValueError,match='CHANGED_PUBLICATION_VIEW'):module.check_publication_chain(tmp_path,case)


@pytest.mark.parametrize('fault',['head','crosscheck'])
def test_orchestrator_rejects_mutated_cache_before_rebasing(tmp_path,monkeypatch,fault):
    def sealed(folder,name,payload):
        raw=encoded(payload);p=tmp_path/folder/sha(raw)/name;p.parent.mkdir(parents=True);p.write_bytes(raw);return p,raw
    cross,body=sealed('outputs/crosscheck','report.json',{'channels':[{'text':'Synthetic original'}]})
    dataset,raw=sealed('outputs/entity-slices','dataset.json',{'dependencies':{cross.relative_to(tmp_path).as_posix():sha(body)}})
    module.write_head(tmp_path,'ops/state/entity-slice-head.json',{'dataset':dataset.relative_to(tmp_path).as_posix(),'sha256':sha(raw)})
    if fault=='head':dataset.write_bytes(b'{}')
    else:cross.write_bytes(encoded({'channels':[{'text':'Changed','text_sha256':sha(b'Changed')}]}))
    monkeypatch.setattr(module,'rebase_publication',lambda *_:pytest.fail('Must reject before advancing base head'))
    with pytest.raises(ValueError,match='CHANGED_ENTITY_CACHE'):module.rebuild_integrated(tmp_path,tmp_path/'unused')


def test_rehashed_crosscheck_replay_cannot_change_ancestor_channels(tmp_path):
    original={'slice_id':'old','channels':[{'text':'Synthetic original'}]}
    body=encoded(original);parent=tmp_path/'cache'/sha(body)/'report.json';parent.parent.mkdir(parents=True);parent.write_bytes(body)
    derived={**original,'slice_id':'new','replayed_from':{'path':parent.relative_to(tmp_path).as_posix(),'sha256':sha(body)},'publication_rebase':'receipt'}
    derived['channels']=[{'text':'Forged','text_sha256':sha(b'Forged')}]
    raw=encoded(derived);child=tmp_path/'cache'/sha(raw)/'report.json';child.parent.mkdir();child.write_bytes(raw)
    with pytest.raises(ValueError,match='CHANGED_CROSSCHECK_REPLAY'):
        module.original_crosscheck(tmp_path,child.relative_to(tmp_path).as_posix(),sha(raw))


def test_failed_atomic_registration_preserves_existing_config(tmp_path,monkeypatch):
    import os
    path=tmp_path/'.eidos/project.yaml';path.parent.mkdir();path.write_bytes(b'original registration')
    def fail(*args):raise OSError('simulated interrupted replace')
    monkeypatch.setattr(os,'replace',fail)
    with pytest.raises(OSError):module.write_atomic(tmp_path,'.eidos/project.yaml',b'new registration')
    assert path.read_bytes()==b'original registration'
    assert list(path.parent.iterdir())==[path]
