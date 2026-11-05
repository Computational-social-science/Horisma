import json
from pathlib import Path

import pytest
import importlib
import itertools

from horisma_p0.fidelity_suite import printed_score, validate_challenge, context_challenge
from horisma_p0.fidelity_blocks import normalize_blocks, normalized_bbox
from horisma_p0.research_slice import encoded,sha
from horisma_p0.probe_artifacts import load_attempt

ROOT=Path(__file__).resolve().parents[2]


def test_frozen_difficult_definitions_and_constructed_contexts():
    challenge=validate_challenge(json.loads((ROOT/'spec/examples/difficult_fidelity_v1.json').read_bytes()))
    rows=context_challenge(challenge)
    assert len(rows)==8 and all(row['passed'] for row in rows)
    assert challenge['historical_gold'] is False


def test_critical_loss_cannot_hide_inside_otherwise_fluent_output():
    text='Harriet Zuckerman [1973], pp. 159–175; did not coin.'
    score=printed_score(text,text.replace('159–175','159175'),['159–175','did not'])
    assert not score['literal_match'] and score['critical_count']==1
    assert not printed_score(text,None,['159–175'])['literal_match']
    assert printed_score('The ﬁeld','The field',[],[['ﬁeld','field']])['literal_match']
    assert not printed_score('José','Jose',['José'])['literal_match']


def test_furniture_and_invalid_charspan_are_retained_without_fake_geometry():
    raw={'pages':{'1':{'size':{'width':100,'height':100}}},'texts':[
        {'self_ref':'#t1','label':'footnote','orig':'old original','text':'[1973]',
         'prov':[{'page_no':1,'charspan':[0,6],'bbox':{'l':1,'t':20,'r':40,'b':10,'coord_origin':'BOTTOMLEFT'}}]},
        {'self_ref':'#t2','label':'page_header','text':'1964','prov':[{'page_no':1,'charspan':[0,9],'bbox':{}}]}]}
    blocks=normalize_blocks('docling',raw,'page')
    assert blocks[0]['text']=='[1973]' and blocks[1]['text']=='1964'
    assert normalized_bbox(blocks[0],100,100)==[.01,.8,.4,.9]
    with pytest.raises(ValueError):normalized_bbox(blocks[1],100,100)


def test_mineru_inline_content_does_not_include_metadata_or_hide_footnotes():
    raw={'pages':[{'blocks':[{'type':'page_footnote','bbox':[0,.8,1,1],
                             'content':[{'type':'text','content':'This is occasion '},
                                        {'type':'text','content':'[1973]'}],
                             'metadata':{'text':'not visible'}}]}]}
    blocks=normalize_blocks('mineru',raw,'region')
    assert blocks[0]['text']=='This is occasion [1973]'
    assert normalized_bbox(blocks[0],100,100)==[0,.8,1,1]


def test_paddle_ocr_geometry_cannot_be_silently_truncated():
    with pytest.raises(ValueError,match='COUNT_MISMATCH'):
        normalize_blocks('paddleocr',{'res':{'rec_texts':['name'],'rec_polys':[]}},'region')


def test_mineru_nested_reference_blocks_preserve_boundaries_and_geometry():
    raw={'pages':[{'blocks':[{'type':'list','content':[
        {'type':'ref_text','bbox':[0,.1,1,.2],'content':[{'type':'text','content':'Harriet Zuckerman'}]},
        {'type':'ref_text','bbox':[0,.3,1,.4],'content':[{'type':'text','content':'Robert K. Merton'}]}]}]}]}
    blocks=normalize_blocks('mineru',raw,'page')
    assert [block['text'] for block in blocks]==['Harriet Zuckerman','Robert K. Merton']
    assert blocks[0]['bbox']!=blocks[1]['bbox']


@pytest.mark.parametrize('mode',['empty-object','array','missing-field','bad-phase-type','timeout','fast-complete'])
def test_monitor_seals_failures_and_counts_fast_completed_jobs(tmp_path,monkeypatch,mode):
    from horisma_p0 import fidelity_campaign as campaign
    suite={'jobs':[{'job_id':'job-one','kind':'region','png_sha256':'input-sha','png_path':'job-one.png'}]}
    protocol={'backends':{'paddleocr':{'version':'3.7.0','runtime':'fake-python'}},'excluded_backends':[],
              'budgets':{'max_initialization_seconds':180,'max_job_seconds':90,'max_backend_seconds':600}}
    monkeypatch.setattr(campaign,'load_suite',lambda *_:(suite,protocol))
    for path in ['.rebuild/fidelity-models/manifest.json','scripts/fidelity_backend_worker.py','src/horisma_p0/fidelity_blocks.py']:
        target=tmp_path/path;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'{}')
    ticks=itertools.count(step=100)
    monkeypatch.setattr(campaign.time,'monotonic',lambda:next(ticks))
    monkeypatch.setattr(campaign.time,'sleep',lambda _:None)

    class Process:
        def __init__(self,command,**kwargs):
            self.returncode=None
            request_path=Path(command[command.index('--request')+1]);request=json.loads(request_path.read_bytes())
            assert set(request['jobs'][0])=={'job_id','kind','png_sha256','png_path'}
            assert (request_path.parent/'model-manifest.json').read_bytes()==b'{}'
            if mode=='fast-complete':
                self.returncode=0;(request_path.parent/'job-one.row.json').write_bytes(b'{}')
            else:
                data={'owner_token':request['owner_token'],'phase':'RUNNING','job_id':'job-one'}
                if mode=='empty-object':data={}
                if mode=='array':data=['invalid']
                if mode=='missing-field':data.pop('phase')
                if mode=='bad-phase-type':data['phase']=[]
                (request_path.parent/'progress.json').write_bytes(encoded(data))
        def poll(self):return self.returncode
        def kill(self):self.returncode=-9
        def wait(self,timeout=None):return self.returncode
    monkeypatch.setattr(campaign.subprocess,'Popen',Process)
    manifest=tmp_path/'outputs/fidelity-suites/suite/manifest.json'
    result=campaign.run_backend(tmp_path,manifest,'paddleocr')
    _,files=load_attempt(tmp_path/'outputs/fidelity-campaigns/paddleocr','suite')
    process=json.loads(files['process.json'])
    assert 'model-manifest.json' in files and not process['scientific_acceptance']
    assert not (tmp_path/'ops/state/research-model-screen.lock').exists()
    if mode=='fast-complete':assert result['started']==1 and result['unrun']==0
    elif mode=='timeout':assert process['status']=='TIMEOUT'
    else:assert process['status']=='INVALID_PROGRESS'


@pytest.mark.parametrize('dimension,rate,status',[
    ('nested-quotation',.6,'ABSTAINED_CRITICAL_DIMENSION_UNRESOLVED'),
    ('citation-and-numbers',1.,'CACHED_REGION_CANDIDATES_ONLY'),
    ('layout',1.,'ABSTAINED_NO_SCOPED_CANDIDATE')])
def test_regional_routes_never_turn_partial_controls_into_qualification(tmp_path,monkeypatch,dimension,rate,status):
    from horisma_p0 import fidelity_report as module
    monkeypatch.setattr(module,'load_suite',lambda *_:({'base_slice_path':'base'},{}))
    codes={}
    for field,name in [('normalizer_sha256','fidelity_blocks.py'),('scoring_operator_sha256','fidelity_suite.py'),('entity_operator_sha256','entity_mentions.py')]:
        path=tmp_path/'src/horisma_p0'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'code')
        codes[field]=sha(b'code')
    report={**codes,'reporter_sha256':sha(Path(module.__file__).read_bytes()),'suite_manifest':'suite','effective_base_slice_path':'base',
            'backends':{},'dimension_candidates':{key:{'candidate_backends':['docling'],'observed_critical_fraction':{'docling':rate}} for key in ['nested-quotation','citation-and-numbers']},
            'historical_region_observations':[{'source_id':'4','backend':'docling','transcript':'unchanged candidate','scientific_acceptance':False}]}
    raw=encoded(report);path=tmp_path/'outputs/fidelity-comparisons'/sha(raw)/'report.json';path.parent.mkdir(parents=True);path.write_bytes(raw)
    result=module.regional_route(tmp_path,path,'4',dimension)
    assert result['status']==status and not result['scientific_acceptance']
    assert result.get('merged_text') is None
    if rate<1:assert result['primary_candidates']==[]
    for field in ['reporter_sha256', *codes]:
        stale={**report,field:'old-code'};body=encoded(stale);stale_path=path.parent.parent/sha(body)/'report.json'
        stale_path.parent.mkdir(exist_ok=True);stale_path.write_bytes(body)
        with pytest.raises(ValueError,match='STALE_'):module.regional_route(tmp_path,stale_path,'4',dimension)
    path.write_bytes(b'{}')
    with pytest.raises(ValueError,match='FIDELITY_REPORT_CHANGED'):module.regional_route(tmp_path,path,'4',dimension)


@pytest.mark.parametrize('status',['SUCCEEDED','FAILED','PARTIAL_OUTPUT'])
def test_failed_or_partial_producer_cannot_enter_candidate_scores(tmp_path,monkeypatch,status):
    from horisma_p0 import fidelity_report as module
    from PIL import Image
    jobs=[];labels={};files={};requests=[]
    for variant in ['clean','downsample-blur']:
        ident='names-'+variant;filename=ident+'.png';Image.new('RGB',(10,10),'white').save(tmp_path/filename)
        jobs.append({'job_id':ident,'synthetic':True,'kind':'region','png_sha256':sha((tmp_path/filename).read_bytes()),'png_path':filename})
        labels[ident]={'expected':'SYN Name','critical':['Name'],'equivalent_classes':[]}
        raw=encoded({'res':{'rec_texts':['SYN Name'],'rec_polys':[[[0,0],[10,0],[10,10],[0,10]]]}})
        files[ident+'.raw.json']=raw
        files[ident+'.row.json']=encoded({'job_id':ident,'input_sha256':jobs[-1]['png_sha256'],'status':status,'elapsed_seconds':1,'raw_output_sha256':sha(raw)})
        requests.append({'job_id':ident,'png_sha256':jobs[-1]['png_sha256']})
    suite={'jobs':jobs,'labels':labels,'base_slice_path':'base'}
    protocol={'backends':['paddleocr'],'historical_sources':[],'challenge':'spec/examples/challenge.json'}
    monkeypatch.setattr(module,'load_suite',lambda *_:(suite,protocol))
    for name in ['fidelity_blocks.py','fidelity_suite.py','entity_mentions.py']:
        p=tmp_path/'src/horisma_p0'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b'code')
    challenge=tmp_path/'spec/examples/challenge.json';challenge.parent.mkdir(parents=True);challenge.write_bytes(b'{}')
    monkeypatch.setattr(module,'context_challenge',lambda *_:[])
    files['model-manifest.json']=b'{}';files['worker-source.py']=b'worker';files['normalizer-source.py']=b'normalizer';files['operator-source.py']=b'operator'
    request=encoded({'suite_id':tmp_path.name,'backend':'paddleocr','jobs':requests,'model_manifest_sha256':sha(b'{}'),'worker_sha256':sha(b'worker'),'normalizer_sha256':sha(b'normalizer')})
    files['request.json']=request;files['process.json']=encoded({'request_sha256':sha(request),'status':'PROCESS_COMPLETED','operator_sha256':sha(b'operator')})
    monkeypatch.setattr(module,'load_attempt',lambda *_:('attempt',files))
    result=module.campaign_report(tmp_path,tmp_path/'manifest.json');report=json.loads(Path(result['report']).read_bytes())
    if status=='SUCCEEDED':
        assert report['backends']['paddleocr']['literal_matches']==2 and 'names' in report['dimension_candidates']
    else:
        assert report['backends']['paddleocr']['synthetic_transcripts']==0 and report['dimension_candidates']=={}
        assert all(row['transcript']=='SYN Name' for row in report['backends']['paddleocr']['rows'])
