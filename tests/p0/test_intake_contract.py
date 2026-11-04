"""Synthetic behavioral checks. They establish no historical truth or OCR fidelity."""
import copy
import json
from pathlib import Path

import pytest
from pypdf import PdfWriter

from horisma_p0.operators import (ContractError, FROZEN_ARTIFACTS, acquire_source,
    check_freeze, digest, index_wikipedia, load_json, owned_path, validate_ledger)


def test_real_frozen_contract_survives_checkout():
    root=Path(__file__).resolve().parents[2]
    check_freeze(root,load_json(root/'spec/p0/freeze_manifest.json'))


@pytest.fixture
def bundle(tmp_path):
    root = Path(__file__).resolve().parents[2]
    schema = load_json(root/'spec/p0/candidate_ledger.schema.json')
    for relative in FROZEN_ARTIFACTS:
        path = tmp_path/relative
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('{}',encoding='utf-8')
    (tmp_path/'spec/p0/candidate_ledger.schema.json').write_text(json.dumps(schema),encoding='utf-8')
    (tmp_path/'spec/controlled_vocabularies.yaml').write_text('vocabularies:\n  contribution_role:\n    codes:\n      LABEL_NAMING: naming\n',encoding='utf-8')
    folder=tmp_path/'data/intake/literature/SYNTHETIC'
    folder.mkdir(parents=True)
    pdf=folder/'source.pdf'
    writer=PdfWriter();writer.add_blank_page(width=200,height=200);writer.write(pdf)
    sha=digest(pdf.read_bytes())
    text='Synthetic fragment anchor for testing.'
    (folder/'private_text.json').write_text(json.dumps({'source_sha256':sha,'pages':[{'raw_text':text}]}),encoding='utf-8')
    (folder/'acquisition.json').write_text(json.dumps({'source_id':'SYNTHETIC','relative_path':'data/intake/literature/SYNTHETIC/source.pdf','expected_media':'pdf','sha256':sha,'access_status':'LOCAL_AVAILABLE'}),encoding='utf-8')
    (folder/'local_draft_v2.json').write_text(json.dumps({'source_id':'SYNTHETIC','source_sha256':sha,'human_approval_granted':False}),encoding='utf-8')
    source={'source_id':'SYNTHETIC','title':'Fictional source, not real evidence','doi':'10.0000/synthetic',
        'version_label':'synthetic test only','media':'pdf','page_count':1,'relative_path':'data/intake/literature/SYNTHETIC/source.pdf',
        'sha256':sha,'source_kind':'PRIMARY_DOCUMENT','identity_status':'UNVERIFIED','rights_status':'NOT_REVIEWED',
        'acquisition_receipt':'data/intake/literature/SYNTHETIC/acquisition.json','discovery_reference_anchor':'cite_note-synthetic'}
    claims=[]
    for i in range(20):
        cid=f'HC-P0-{i+1:03}'
        claims.append({'candidate_id':cid,'source_id':'SYNTHETIC','proposition_en':f'Fictional atomic proposition {i}; not an actual source assertion.',
            'claim_class':'THEORY','locator':{'kind':'PDF_PAGE_REGION','source_sha256':sha,'pdf_page_index':0,
                'region':[0,0,1,1],'anchor_quote':'Synthetic fragment anchor','transcription_review_status':'PENDING',
                'derivative_receipt':'data/intake/literature/SYNTHETIC/private_text.json','normalized_page_sha256':digest(text.encode()),'text_start':0,'text_end':25,'context_start':0,'context_end':len(text)},
            'formalization':{'predicate':'SOURCE_ASSERTS','arguments':['SYNTHETIC',cid]},'qualification':'Synthetic fixture; no source fidelity review.',
            'origin':'MODEL_PROPOSED','contribution_role':None,'explicit_exclusivity_asserted':False,'assessment':None,
            'review_status':'PENDING','proof_status':'UNPROVEN','missing_reasons':{'assessment':'NOT_ASSESSED','contribution_role':'NOT_APPLICABLE'},
            'local_draft_receipt':'data/intake/literature/SYNTHETIC/local_draft_v2.json','citation_trace_status':'NOT_COLLECTED',
            'proposal_provenance':'MAIN_MODEL_CURATED_FROM_SCHOLARLY_BODY_LOCAL_PARSE; LOCAL_REWRITES_NOT_ACCEPTED'})
    ledger={'profile_version':'1.0.0','scope':'SCHOLARLY_CLAIM_CANDIDATES_NOT_GOLD','disclosure_class':'INTERNAL',
      'predicate_registry':{'SOURCE_ASSERTS':{'arity':2,'signature':'DocumentVersion x CandidateClaim -> SourceReportingProposition',
        'interpretation':'Synthetic proposed source-reporting formula, not a historical truth.'}},'literature_sources':[source],'candidates':claims}
    manifest={'kind':'ENGINEERING_CONTRACT_FREEZE_NOT_SCIENTIFIC_APPROVAL',
       'sha256':{relative:digest((tmp_path/relative).read_bytes()) for relative in FROZEN_ARTIFACTS}}
    return tmp_path,ledger,schema,manifest


def test_valid_binding_never_grants_scientific_approval(bundle):
    result=validate_ledger(*bundle)
    assert result['candidate_count']==20
    assert result['scientific_adjudication_performed'] is False
    assert result['human_approval_granted'] is False
    assert result['formal_proof_performed'] is False


@pytest.mark.parametrize(('mutation','reason'),[
    ('source','LITERATURE_BYTES_CHANGED'),('wiki','NON_SCHOLARLY_CLAIM_SOURCE'),
    ('page','PDF_PAGE_OUT_OF_RANGE'),('quote','TEXT_ANCHOR_MISMATCH'),
    ('derivative','TEXT_DERIVATIVE_CHANGED'),('duplicate','DUPLICATE_CLAIM_ID'),
    ('argument','FORMAL_ARGUMENT_BINDING_MISMATCH'),('approval','SCHEMA_INVALID'),
    ('assessment','SCHEMA_INVALID'),('empty_freeze','FREEZE_ARTIFACT_SET_MISMATCH'),
    ('receipt','ACQUISITION_RECEIPT_MISMATCH'),('draft','DRAFT_RECEIPT_MISMATCH')])
def test_negative_controls_fail_for_intended_reason(bundle,mutation,reason):
    root,ledger,schema,freeze=bundle
    if mutation=='source':(root/ledger['literature_sources'][0]['relative_path']).write_bytes(b'changed')
    elif mutation=='wiki':ledger['literature_sources'][0]['source_kind']='TERTIARY_ENCYCLOPEDIA'
    elif mutation=='page':ledger['candidates'][0]['locator']['pdf_page_index']=1
    elif mutation=='quote':ledger['candidates'][0]['locator']['anchor_quote']='invented quotation'
    elif mutation=='derivative':ledger['candidates'][0]['locator']['normalized_page_sha256']='0'*64
    elif mutation=='duplicate':ledger['candidates'][1]['candidate_id']=ledger['candidates'][0]['candidate_id']
    elif mutation=='argument':ledger['candidates'][0]['formalization']['arguments'][0]='OTHER_SOURCE'
    elif mutation=='approval':ledger['candidates'][0]['review_status']='APPROVED'
    elif mutation=='assessment':ledger['candidates'][0]['assessment']='SUPPORTED'
    elif mutation=='empty_freeze':freeze['sha256']={}
    elif mutation=='receipt':
        path=root/'data/intake/literature/SYNTHETIC/acquisition.json';value=load_json(path);value['source_id']='OTHER';path.write_text(json.dumps(value),encoding='utf-8')
    elif mutation=='draft':
        path=root/'data/intake/literature/SYNTHETIC/local_draft_v2.json';value=load_json(path);value['source_sha256']='0'*64;path.write_text(json.dumps(value),encoding='utf-8')
    with pytest.raises(ContractError,match=reason):validate_ledger(root,ledger,schema,freeze)


def test_frozen_definition_change_refuses(bundle):
    root,ledger,schema,freeze=bundle
    (root/'spec/p0/protocol.json').write_text('changed',encoding='utf-8')
    with pytest.raises(ContractError,match='FROZEN_CONTRACT_CHANGED'):validate_ledger(root,ledger,schema,freeze)


def test_doi_grouping_preserves_citation_instances_and_unicode():
    payload='''<script>{"wgRevisionId":123}</script><div class="mw-parser-output"><ol class="references">
      <li id="cite_note-a">Matjaž <a class="external" href="https://doi.org/10.0000%2FTest">DOI</a></li>
      <li id="cite_note-b">second instance <a class="external" href="https://doi.org/10.0000/test">DOI</a></li>
      </ol></div>'''.encode()
    result=index_wikipedia(payload,digest(payload),'123')
    assert result['proposed_work_groups']==1
    assert len(result['reference_entries'])==2
    assert 'Matjaž' in result['reference_entries'][0]['citation_text']
    with pytest.raises(ContractError,match='REVISION_MISMATCH'):index_wikipedia(payload,digest(payload),'124')


def test_source_denial_creates_wait_without_retry(tmp_path,monkeypatch):
    from urllib.error import HTTPError
    calls=[]
    class Denied:
        def open(self,*args,**kwargs):
            calls.append(1)
            raise HTTPError('https://arxiv.org/test',403,'denied',None,None)
    monkeypatch.setattr('horisma_p0.operators.build_opener',lambda *args:Denied())
    result=acquire_source(tmp_path,'SYNTHETIC','https://arxiv.org/test','pdf')
    assert result['access_status']=='WAITING_HUMAN_SOURCE'
    assert result['failure_kind']=='ACCESS_DENIED'
    assert result['public_redistribution_authorized'] is False
    assert acquire_source(tmp_path,'SYNTHETIC','https://arxiv.org/test','pdf')==result
    assert len(calls)==1


def test_unapproved_endpoint_and_cross_project_write_refused(tmp_path):
    with pytest.raises(ContractError,match='SOURCE_URL_NOT_ALLOWLISTED'):
        acquire_source(tmp_path,'SYNTHETIC','https://127.0.0.1/private','pdf')
    with pytest.raises(ContractError,match='PATH_OUTSIDE_PROJECT'):owned_path(tmp_path,'../Eidos/state/x')


def test_duplicate_json_keys_are_refused(tmp_path):
    path=tmp_path/'duplicate.json';path.write_text('{"x":1,"x":2}',encoding='utf-8')
    with pytest.raises(ContractError,match='DUPLICATE_JSON_KEY'):load_json(path)


def test_local_model_redirect_is_refused():
    from urllib.request import Request
    from horisma_p0.local_documents import NoModelRedirects
    with pytest.raises(ContractError,match='MODEL_REDIRECT_REFUSED'):
        NoModelRedirects().redirect_request(Request('http://127.0.0.1:8081/v1/chat/completions'),None,302,'redirect',{},'https://external.invalid/model')


def test_malformed_local_output_is_preserved_and_quarantined(tmp_path,monkeypatch):
    from horisma_p0.local_documents import draft_locally
    class FakeResponse:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,*args):return b'{"choices":[{"message":{"content":"[]"}}]}'
    class Opener:
        def open(self,*args,**kwargs):return FakeResponse()
    monkeypatch.setattr('horisma_p0.local_documents.build_opener',lambda *args:Opener())
    result=draft_locally(tmp_path,{'source_id':'SYNTHETIC','source_sha256':'0'*64,'pages':[{'pdf_page_index':0,'raw_text':'Synthetic text only.'}]},'synthetic-local-model')
    assert result['candidates']==[] and result['model_output_shape_rejected']
    assert result['human_approval_granted'] is False
    assert (tmp_path/'data/intake/literature/SYNTHETIC/local_draft_v2.raw').is_file()
