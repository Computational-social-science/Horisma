import json
import pytest
from horisma_p0.evidence_audit import bound_excerpt,index_bracket_references,propose_text_score,check_cached_audit
from horisma_p0.operators import ContractError


def test_unicode_matching_preserves_offsets_and_source_binding():
    extraction={'source_sha256':'a'*64,'pages':[{'raw_text':'ﬁ ligature before TARGET assertion.'}]}
    result=bound_excerpt(extraction,0,'target',2)
    assert 'TARGET' in result['text'] and result['source_sha256']=='a'*64
    with pytest.raises(ContractError,match='AUDIT_ANCHOR_NOT_FOUND'):bound_excerpt(extraction,0,'missing')
    with pytest.raises(ContractError,match='AUDIT_PAGE_OR_RADIUS_INVALID'):bound_excerpt(extraction,-1,'TARGET')


def test_reference_index_is_document_scoped_and_not_support():
    source={'source_sha256':'a'*64,'pages':[{'pdf_page_index':0,'raw_text':'[1] Author A. Title (1965). [2] de Solla Price. Another title.'}]}
    result=index_bracket_references(source,0)
    assert set(result)=={'1','2'} and result['1']['boundary_review_required']
    assert result['1']['source_sha256']=='a'*64


@pytest.mark.parametrize('score,valid',[(2,True),(0,False)])
def test_model_ordinal_is_checked_without_granting_truth(monkeypatch,score,valid):
    payload={'choices':[{'message':{'content':json.dumps({'relation':'DIRECT_AUTHOR_STATEMENT','score':score})}}]}
    class Reply:
        def __enter__(self):return self
        def __exit__(self,*args):pass
        def read(self,*args):return json.dumps(payload).encode()
    class Opener:
        def open(self,*args,**kwargs):return Reply()
    monkeypatch.setattr('horisma_p0.evidence_audit.build_opener',lambda *args:Opener())
    result=propose_text_score('Synthetic proposition',[{'text':'Synthetic context'}],'synthetic-local-model')
    assert (result['proposal'] is not None)==valid
    assert result['historical_assessment'] is None and result['human_approval_granted'] is False
    if valid:
        row={'proposition_en':'Synthetic proposition','excerpts':[{'text':'Synthetic context'}],'local_model_text_fit':result}
        check_cached_audit(row,'Synthetic proposition',row['excerpts'],'synthetic-local-model')
        with pytest.raises(ContractError,match='STALE_AUDIT_CACHE_BINDING'):
            check_cached_audit(row,'Changed proposition',row['excerpts'],'synthetic-local-model')
