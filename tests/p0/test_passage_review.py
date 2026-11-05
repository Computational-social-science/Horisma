import json
from pathlib import Path
import pytest
from horisma_p0.passage_review import bind_passage, reusable_row
from horisma_p0.research_slice import encoded, sha


def test_rebinding_respects_unit_boundary_and_never_rewrites_text(tmp_path):
    text='Adjacent unrelated article.\nThe conception draws on interviews with Ada; other scientists.\nLater other scientists.'
    (tmp_path/'paper.md').write_bytes(text.encode())
    lo=text.index('The conception');hi=text.index('\nLater')
    mapping={'markdown_sha256':sha(text.encode()),'source_sha256':'source',
             'units':[{'markdown_unicode_span':[lo,hi],'unit_id':'syn:unit','bbox_pdf_points':[0,0,10,10],'pdf_page_index':0}]}
    (tmp_path/'map.json').write_bytes(encoded(mapping))
    node={'context_artifact':'paper.md','locator_map':'map.json','source_version_ref':'syn:source@source'}
    result=bind_passage(tmp_path,node,'The conception','other scientists.')
    assert result['context_span']==[lo,hi]
    assert (tmp_path/'paper.md').read_bytes()==text.encode()
    assert result['qualification_ref'] is None
    with pytest.raises(ValueError,match='WRONG_PASSAGE_SOURCE_VERSION'):
        bind_passage(tmp_path,{**node,'source_version_ref':'syn:source@wrong'},'The conception','other scientists.')
    with pytest.raises(ValueError):bind_passage(tmp_path,node,'Adjacent','interviews')


def cached(tmp_path):
    packet={'text':'Synthetic source','id':'syn'};body={'model':'local','prompt':'bounded'};ids={'local':'digest'}
    recipe={'models':ids};raw=encoded(recipe);folder=tmp_path/'outputs/passage-reviews'/sha(raw);folder.mkdir(parents=True)
    (folder/'recipe.json').write_bytes(raw)
    row={'packet_sha256':sha(encoded(packet)),'request':body,'model':'startlux','status':'VALID_DIAGNOSTIC','scientific_acceptance':False,
         'raw_response':json.dumps({'choices':[{'message':{'content':json.dumps({'decision':'SUPPORTED','quote':'Synthetic source'})}}]})}
    (folder/'row.json').write_bytes(encoded(row))
    report={'recipe_sha256':sha(raw),'artifacts':{(folder/'row.json').relative_to(tmp_path).as_posix():sha(encoded(row))}}
    rp=folder/'report.json';rp.write_bytes(encoded(report));head={'report':rp.relative_to(tmp_path).as_posix(),'sha256':sha(encoded(report))}
    return packet,body,ids,head,folder


@pytest.mark.parametrize('change',[None,'packet','request','model','row','report','recipe'])
def test_only_identical_bound_inference_can_be_reused(tmp_path,change):
    packet,body,ids,head,folder=cached(tmp_path)
    if change=='packet':packet['text']='Different source'
    if change=='request':body['prompt']='Different task'
    if change=='model':ids={'local':'different weights'}
    if change in {'row','report','recipe'}:
        (folder/(change+'.json')).write_bytes(b'{}')
        with pytest.raises(ValueError):reusable_row(tmp_path,head,packet,body,ids)
    else:
        result=reusable_row(tmp_path,head,packet,body,ids)
        assert (result is not None)==(change is None)
        if result:assert result['inference_reused'] and not result['scientific_acceptance']


def test_cached_raw_answer_is_revalidated_with_current_validator(tmp_path,monkeypatch):
    from horisma_p0 import passage_review
    packet,body,ids,head,folder=cached(tmp_path)
    monkeypatch.setattr(passage_review,'validate_answer',lambda *_:None)
    row=reusable_row(tmp_path,head,packet,body,ids)
    assert row['answer'] is None and row['status']=='INVALID_RESPONSE'


def test_review_cannot_be_current_after_transitive_source_change(tmp_path):
    from horisma_p0.passage_review import check_review
    from horisma_p0.publication_rebase import write_head
    packet,body,ids,head,folder=cached(tmp_path)
    source=tmp_path/'source.md';source.write_bytes(b'original synthetic source')
    case=encoded({'case_id':'syn:case','dependencies':{'source.md':sha(source.read_bytes())}})
    path=tmp_path/'outputs/attribution-cases'/sha(case)/'case.json';path.parent.mkdir(parents=True);path.write_bytes(case)
    write_head(tmp_path,'ops/state/attribution-case-head.json',{'case':path.relative_to(tmp_path).as_posix(),'sha256':sha(case)})
    write_head(tmp_path,'ops/state/passage-review-head.json',head)
    source.write_bytes(b'changed source, unchanged declared case head')
    with pytest.raises(ValueError,match='STALE_REVIEW_CASE'):check_review(tmp_path)
