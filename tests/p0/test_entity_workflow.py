import json
from pathlib import Path

import pytest
import yaml

from horisma_p0 import entity_workflow as workflow
from horisma_p0.entity_sources import validate_authority_index, acquire_entity_sources
from horisma_p0.research_slice import encoded, sha


def fixture(root):
    def put(path, value):
        path=root/path;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(value if isinstance(value,bytes) else encoded(value));return path

    def claim(qid,prop,value,suffix='a'):
        return {'id':qid+'$'+prop+suffix,'rank':'normal','mainsnak':{'snaktype':'value','datavalue':{'value':value}}}

    config={'entities':[{'entity_ref':'P1','entity_kind':'PERSON','wikidata_id':'Q1','wikipedia_title':'Harriet Zuckerman'},
                        {'entity_ref':'C1','entity_kind':'CONCEPT','wikidata_id':'Q6','wikipedia_title':'Matthew effect'}],
            'languages':['en','zh'],'concept_family_ref':'family'}
    put(workflow.CATALOG,config)
    put('spec/extensions/term_aliases.yaml',{'related_mechanism_forms':['accumulated advantage']})
    original=Path(__file__).resolve().parents[2]
    for name in workflow.CODE_PATHS:
        if not (root/name).exists():put(name,(original/name).read_bytes())
    nodes={
        'Q1':{'labels':{'en':{'value':'Harriet Zuckerman','language':'en'}},
              'aliases':{'en':[{'value':'Harriet A. Zuckerman','language':'en'}]},
              'claims':{'P735':[claim('Q1','P735',{'id':'Q2'})],
                        'P734':[claim('Q1','P734',{'id':'Q3'})],
                        'P27':[claim('Q1','P27',{'id':'Q4'})]}},
        'Q2':{'labels':{'en':{'value':'Harriet','language':'en'}}},
        'Q3':{'labels':{'en':{'value':'Zuckerman','language':'en'}}},
        'Q4':{'claims':{'P297':[claim('Q4','P297','US')]}},
        'Q6':{'labels':{'en':{'value':'Matthew effect','language':'en'}},
              'aliases':{'en':[{'value':'accumulated advantage','language':'en'}]}}
    }
    records={}
    for qid,node in nodes.items():
        node.update(id=qid,lastrevid=1)
        raw=encoded({'entities':{qid:node}});path=put('data/authority/'+qid+'.json',raw)
        records[qid]={'qid':qid,'revision_id':1,'blob':{'path':path.relative_to(root).as_posix(),'sha256':sha(raw)}}
    pages={str(i):{'title':entry['wikipedia_title'],'pageprops':{'wikibase_item':entry['wikidata_id']}} for i,entry in enumerate(config['entities'])}
    raw=encoded({'query':{'pages':pages}});path=put('data/authority/binding.json',raw)
    index={'catalog_sha256':sha((root/workflow.CATALOG).read_bytes()),'entities':records,
           'wikipedia_binding':{'mapping':{entry['wikipedia_title']:entry['wikidata_id'] for entry in config['entities']},
                                'blob':{'path':path.relative_to(root).as_posix(),'sha256':sha(raw)}}}
    put(workflow.INDEX,index)
    put(workflow.FLAG_ROOT+'/country.json',[{'code':'us','iso':True,'flag_4x3':'flags/4x3/us.svg'}])
    put(workflow.FLAG_ROOT+'/package.json',{'name':'flag-icons','version':'synthetic','license':'MIT'})
    put(workflow.FLAG_ROOT+'/LICENSE',b'synthetic MIT fixture')
    flag=put(workflow.FLAG_ROOT+'/flags/4x3/us.svg',b'<svg/>')
    native=b'Harriet Zuckerman studied the Matthew effect. She wrote.'
    native_path=put('data/intake/derived/evidence-vault/native',native)
    base={'sources':{'3':{'version_id':'work@v1','sha256':'source'}},
          'regions':{'3':{'region_id':'region','page_index':0,'native_text_blob':{'path':native_path.relative_to(root).as_posix(),'sha256':sha(native)}}},
          'people':[{'person_id':'P1','preferred_name':'Harriet Zuckerman','assertion_refs':[]}],
          'tasks':[{'task_id':'task','revision':'r1','sources':{'3':{}},'gold_answer':None}]}
    folder=root/'outputs/research-slices/base';folder.mkdir(parents=True)
    (folder/'slice.json').write_bytes(encoded(base))
    return folder,index,config,flag


def test_rebuild_and_name_source_provenance_and_flag_binding(tmp_path,monkeypatch):
    folder,index,config,flag=fixture(tmp_path)
    monkeypatch.setattr(workflow,'check_slice',lambda *_:{'preview_eligible':True})
    first=workflow.build_entity_dataset(tmp_path,folder)
    assert workflow.build_entity_dataset(tmp_path,folder)['dataset']==first['dataset']
    data=json.loads(Path(first['dataset']).read_bytes())
    assert first['scientists']==1 and first['flag_assets']==1 and first['benchmark_tasks']==1
    assert any(form['relation']=='RELATED_MECHANISM' and not form['linkable'] for form in data['forms'])
    assert not any(mention['literal_text']=='accumulated advantage' for p in data['passages'] for mention in p['mentions'])
    for form in data['forms']:
        value=json.loads((tmp_path/form['source_blob']['path']).read_bytes())
        for part in form['passage_or_region_ref'].split('/')[1:]:
            value=value[int(part)] if isinstance(value,list) else value[part]
        assert value==form['literal_form']
        assert form['character_span']==[0,len(value)] and not form['identity_qualified']
    assert data['flag_assets'][0]['path']==flag.relative_to(tmp_path).as_posix()
    assert not data['flag_assets'][0]['display_eligible']
    context_ids={context['context_id'] for passage in data['passages'] for context in passage['contexts']}
    mention_ids={mention['mention_id'] for passage in data['passages'] for mention in passage['mentions']}
    entity_ids={'P1','C1'}
    for passage in data['passages']:
        for observation in passage['mentions']+passage['coreferences']:
            assert set(observation['context_refs'])<=context_ids
            assert observation['source_version_ref']=='work@v1'
            assert observation['passage_or_region_ref']=='region'
        for coref in passage['coreferences']:
            assert set(coref['antecedent_mention_refs'])<=mention_ids
    assert all(edge['target_ref'] in entity_ids and not edge['accepted'] for edge in data['evidence_edges'])
    assert workflow.check_entity_dataset(tmp_path,Path(first['dataset']))['preview_eligible']
    flag.write_bytes(b'changed flag')
    assert not workflow.check_entity_dataset(tmp_path,Path(first['dataset']))['preview_eligible']


@pytest.mark.parametrize('defect',['binding-bytes','swapped-key','mapping','catalog-binding'])
def test_offline_authority_cache_rejects_changed_binding(tmp_path,defect):
    _,index,config,_=fixture(tmp_path)
    if defect=='binding-bytes':
        (tmp_path/index['wikipedia_binding']['blob']['path']).write_bytes(b'changed')
    elif defect=='swapped-key':index['entities']['Q1']=index['entities']['Q2']
    elif defect=='mapping':index['wikipedia_binding']['mapping']['Harriet Zuckerman']='Q2'
    else:config['entities'][0]['wikidata_id']='Q2'
    with pytest.raises(ValueError):validate_authority_index(tmp_path,index,config)


def test_source_updates_invalidate_projections_without_inventing_labels(tmp_path,monkeypatch):
    folder,index,_,_=fixture(tmp_path)
    monkeypatch.setattr(workflow,'check_slice',lambda *_:{'preview_eligible':True})
    built=workflow.build_entity_dataset(tmp_path,folder)
    path=tmp_path/index['entities']['Q1']['blob']['path'];path.write_bytes(path.read_bytes()+b' ')
    stale=workflow.check_entity_dataset(tmp_path,Path(built['dataset']))
    assert not stale['preview_eligible'] and 'benchmark' in stale['affected_projections']
    assert not stale['scientific_eligible']


def test_cached_acquisition_is_offline(tmp_path,monkeypatch):
    fixture(tmp_path)
    import horisma_p0.entity_sources as sources
    monkeypatch.setattr(sources,'public_json',lambda *_:pytest.fail('offline cache contacted network'))
    assert acquire_entity_sources(tmp_path)['network_requests']==0
