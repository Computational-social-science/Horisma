import json
import pytest
from horisma_p0.regional_qualification import line_witness,score_constructed,validate_definition,validate_frozen_inputs


def raw_lines():
    return {'res':{'width':100,'height':100,'doc_preprocessor_res':{'angle':0},
                   'overall_ocr_res':{'rec_texts':['Harriet Zucker-','man (I) said: "I did not coin it."'],
                                      'rec_polys':[[[5,10],[90,10],[90,20],[5,20]],[[5,25],[90,25],[90,35],[5,35]]]}}}


def test_line_witness_preserves_literal_defects_and_does_not_certify():
    raw=raw_lines();result=line_witness(raw,[.1,.05,.95,.4])
    assert result['transcript']=='Harriet Zucker-\nman (I) said: "I did not coin it."'
    assert result['boundary_crossing_lines']==2
    assert result['fidelity_qualified'] is False
    assert '(1)' not in result['transcript']


@pytest.mark.parametrize('fault',['rotation','dimension','length','bounds'])
def test_invalid_cached_geometry_is_not_repaired_or_clipped(fault):
    raw=raw_lines()
    if fault=='rotation':raw['res']['doc_preprocessor_res']['angle']=90
    if fault=='dimension':raw['res']['width']=0
    if fault=='length':raw['res']['overall_ocr_res']['rec_texts'].pop()
    if fault=='bounds':raw['res']['overall_ocr_res']['rec_polys'][0][0][0]=-1
    with pytest.raises(ValueError):line_witness(raw,[0,0,1,1])


@pytest.mark.parametrize('fault',[None,'speaker','decision','quote','anchor','schema'])
def test_constructed_scoring_requires_role_speaker_and_literal_evidence(fault):
    case={'text':'A writes: "B said, \'I did not coin Aster.\'"', 'expected_decision':'CONTRADICTED',
          'expected_speaker':'B','evidence_anchor':'I did not coin'}
    answer={'decision':'CONTRADICTED','quote':'I did not coin Aster.','speaker':'B'}
    if fault=='speaker':answer['speaker']='A'
    if fault=='decision':answer['decision']='SUPPORTED'
    if fault=='quote':answer['quote']='I coined Aster.'
    if fault=='anchor':answer['quote']='Aster.'
    if fault=='schema':answer['confidence']=1
    result=score_constructed(json.dumps(answer),case)
    assert result['passed']==(fault is None)


def test_invalid_target_is_rejected_before_selection():
    with pytest.raises(ValueError):line_witness(raw_lines(),[0,0,2,1])


@pytest.mark.parametrize('fault',[None,'budget','dimension','labels','anchor','count','synthetic'])
def test_holdout_definition_is_validated_before_runtime(fault):
    cases=[{'id':str(i),'dimension':'ROLE' if i<6 else 'NESTED_QUOTE','synthetic':True,'text':'Synthetic evidence',
            'claim':'A constructed claim','expected_decision':'NOT_ESTABLISHED','expected_speaker':'NOT_APPLICABLE','evidence_anchor':'evidence'} for i in range(12)]
    corpus={'seed':7,'historical_gold':False,'cases':cases}
    freeze={'seed':7,'case_count':12,'dimensions':{'ROLE':6,'NESTED_QUOTE':6},'request_timeout_seconds':45,'run_budget_seconds':300}
    if fault=='budget':freeze['run_budget_seconds']=10000
    if fault=='dimension':cases[0]['dimension']='OTHER'
    if fault=='labels':cases[0]['expected_decision']='PASS'
    if fault=='anchor':cases[0]['evidence_anchor']='Absent'
    if fault=='count':cases.pop()
    if fault=='synthetic':cases[0]['synthetic']=False
    if fault is None:validate_definition(freeze,corpus)
    else:
        with pytest.raises(ValueError):validate_definition(freeze,corpus)


def test_same_version_label_and_freeze_rewrite_is_rejected(tmp_path):
    path=tmp_path/'spec/extensions/role_quote_holdout_v1.lock.json';path.parent.mkdir(parents=True);path.write_bytes(b'{}')
    with pytest.raises(ValueError,match='NEW_VERSION_REQUIRED'):validate_frozen_inputs(tmp_path,b'{}',b'{}')


def test_regional_summary_is_not_current_after_transitive_source_change(tmp_path):
    from horisma_p0.regional_qualification import check_qualification
    from horisma_p0.publication_rebase import write_head
    from horisma_p0.research_slice import encoded,sha
    source=tmp_path/'source';source.write_bytes(b'original')
    data=encoded({'case_id':'syn:case','dependencies':{'source':sha(b'original')}})
    path=tmp_path/'outputs/attribution-cases'/sha(data)/'case.json';path.parent.mkdir(parents=True);path.write_bytes(data)
    write_head(tmp_path,'ops/state/attribution-case-head.json',{'case':path.relative_to(tmp_path).as_posix(),'sha256':sha(data)})
    source.write_bytes(b'changed')
    with pytest.raises(ValueError,match='STALE_QUALIFICATION_CASE'):check_qualification(tmp_path)
