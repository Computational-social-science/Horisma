import json
from pathlib import Path
import pytest

from horisma_p0.json_contracts import compile_contracts,validate_interchange,DIRECTORY,DICTIONARY,VOCAB
from horisma_p0.research_slice import encoded,sha


@pytest.fixture(scope='module')
def workspace(tmp_path_factory):
    root=tmp_path_factory.mktemp('json-contracts');project=Path(__file__).resolve().parents[2]
    for p in [DICTIONARY,VOCAB,'spec/p0/freeze_manifest.json']:
        target=root/p;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((project/p).read_bytes())
    compile_contracts(root)
    return root


def actor():
    uid='00000000-0000-4000-8000-000000000001';ref='record:'+uid
    return {'schema_profile':'horisma-dictionary-structural-0.1.0','record_type':'actor','definition_stage':'CORE_CONTRACT_DEFINED',
            'record':{'entity_id':'actor:'+uid,'record_id':ref,'record_version':1,'dictionary_version':'0.1.0','vocabulary_version':'0.1.0',
                      'record_status':'DRAFT','created_at':'2026-11-05T00:00:00Z','created_by_actor_ref':ref,'disclosure_class':'INTERNAL',
                      'supersedes_record_id':None,'authorization_artifact_ref':None,'provenance_artifact_refs':[],
                      'display_label':'Synthetic software actor','kind':'SOFTWARE',
                      'missing_reasons':{'/supersedes_record_id':'NOT_APPLICABLE','/authorization_artifact_ref':'NOT_ASSESSED'}}}


def citation(root):
    text='Synthetic source, unchanged.';(root/'source.md').write_bytes(text.encode())
    bound={'record_id':'synthetic:source','revision_sha256':'0'*64,'binding_kind':'SOURCE_BYTES'}
    record={'schema_profile':'horisma-citation-object-0.1.0','citation_id':'citation:synthetic','witness_work_ref':bound,
        'witness_version_ref':bound,'authors':None,'author_list_complete':False,'source_kind':'PRIMARY_DOCUMENT',
        'source_locator':{'pdf_page_index':0,'printed_page':None,'normalized_region':[0,0,1,1]},
        'reading_binding':{'artifact':{'path':'source.md','sha256':sha(text.encode())},'unicode_start':0,'unicode_end':len(text),'offset_unit':'UNICODE_CODE_POINTS_IN_EXACT_UTF8_TEXT'},
        'reading_text':text,'diplomatic_text':None,'reading_entry_status':'PAPER2SKILL_BOUND','related_passage_refs':[],
        'normalization_operations':[],'abbreviations':None,'citation_mode':'DIRECT_SOURCE_TEXT','referenced_work_ref':None,
        'referenced_original_inspected':False,'evidence_group_ref':'source:synthetic','source_identity_status':'UNVERIFIED',
        'confidence':None,'confidence_missing_reason':'NOT_ASSESSED','support_scope':'Synthetic only',
        'missing_reasons':{'/authors':'NOT_COLLECTED','/source_locator/printed_page':'NOT_ASSESSED','/diplomatic_text':'NOT_ASSESSED','/abbreviations':'NOT_COLLECTED','/referenced_work_ref':'NOT_APPLICABLE','/confidence':'NOT_ASSESSED'},
        'scientific_acceptance':False,'publication_authorized':False}
    record['revision_sha256']=sha(encoded(record));return record


def test_full_dictionary_coverage_and_deterministic_compilation(workspace):
    folder=workspace/DIRECTORY;index=json.loads((folder/'index.json').read_bytes())
    assert index['core_entities']==55 and index['extension_entities']==6
    assert len(index['entries'])==61
    before={p.name:sha(p.read_bytes()) for p in folder.glob('*.json')}
    compile_contracts(workspace)
    assert before=={p.name:sha(p.read_bytes()) for p in folder.glob('*.json')}
    template=json.loads((folder/'actor.template.json').read_bytes())
    assert template['template_only'] is True
    document=actor();document['record']=template['record_skeleton']
    with pytest.raises(ValueError):validate_interchange(workspace,document)


def test_valid_structure_never_grants_scientific_acceptance(workspace):
    result=validate_interchange(workspace,actor())
    assert result['structurally_valid'] and not result['scientific_acceptance']
    assert result['reference_resolution']=='NOT_CHECKED'


@pytest.mark.parametrize('fault',['status','namespace','unknown','null','omitted','pointer','unrelated','known','absent-parent','nan','root','type','datetime'])
def test_invalid_records_and_missingness_scope_are_rejected(workspace,fault):
    document=actor();record=document['record']
    if fault=='status':record['record_status']='SUCCEEDED'
    if fault=='namespace':record['entity_id']=record['entity_id'].replace('actor:','contributor:')
    if fault=='unknown':record['invented_field']='value'
    if fault=='null':record['display_label']=None
    if fault=='omitted':del record['authorization_artifact_ref'];del record['missing_reasons']['/authorization_artifact_ref']
    if fault=='pointer':record['missing_reasons']['not-a-pointer']='UNKNOWN'
    if fault=='unrelated':record['missing_reasons']['/unrelated_metric']='UNKNOWN'
    if fault=='known':record['missing_reasons']['/display_label']='UNKNOWN'
    if fault=='absent-parent':record['missing_reasons']['/authorization_artifact_ref/child']='UNKNOWN'
    if fault=='nan':record['record_version']=float('nan')
    if fault=='root':document=[]
    if fault=='type':document['record_type']=42
    if fault=='datetime':record['created_at']='not-a-recording-time'
    with pytest.raises(ValueError):validate_interchange(workspace,document)


@pytest.mark.parametrize('fault',[None,'artifact','span','float-offset','revision','indirect','identity-status','confidence','region','nested-missing'])
def test_citation_bytes_source_scope_and_unknowns(workspace,fault):
    record=citation(workspace)
    if fault=='artifact':(workspace/'source.md').write_bytes(b'changed source')
    if fault=='span':record['reading_binding']['unicode_start']=1
    if fault=='float-offset':record['reading_binding']['unicode_start']=0.0
    if fault=='revision':record['support_scope']='Changed without revision'
    if fault=='indirect':record['citation_mode']='INDIRECT_QUOTATION'
    if fault=='identity-status':record['source_identity_status']='APPROVED'
    if fault=='confidence':record['confidence']=0.99
    if fault=='region':record['source_locator']['normalized_region']=[.8,0,.2,1]
    if fault=='nested-missing':del record['missing_reasons']['/source_locator/printed_page']
    if fault is None:assert validate_interchange(workspace,record)['structurally_valid']
    else:
        with pytest.raises(ValueError):validate_interchange(workspace,record)
