from horisma_p0.paragraph_triage import retrieve_attribution_candidates,link_numeric_citations
from horisma_p0.operators import ContractError
import pytest


def test_literal_retrieval_returns_candidates_without_promoting_or_deleting():
    paragraphs=[{'paragraph_id':'a','text':'The Matthew effect was coined by fictional Scholar A [1].'},
       {'paragraph_id':'b','text':'An unrelated term was coined elsewhere.'},
       {'paragraph_id':'c','text':'The Matthew effect concerns cumulative advantage.'}]
    result=retrieve_attribution_candidates(paragraphs,['Matthew effect'],'a'*64)
    assert [r['paragraph_id'] for r in result]==['a']
    assert len(paragraphs)==3 and result[0]['support_assessment'] is None


def test_citation_linkage_keeps_unresolved_and_never_claims_support():
    result=link_numeric_citations('A synthetic claim [1, 2].',{'1':{'source_sha256':'a'*64,'reference_id':'r1'}},'a'*64)
    assert [r['link_status'] for r in result]==['LINKED_NOT_VERIFIED','UNRESOLVED']
    assert all(r['relation']=='CITES_CANDIDATE' and r['support_assessment'] is None for r in result)


def test_cross_document_marker_collision_is_rejected():
    with pytest.raises(ContractError,match='CITATION_DOCUMENT_MISMATCH'):
        link_numeric_citations('[1]',{'1':{'source_sha256':'b'*64,'reference_id':'wrong'}},'a'*64)


def test_missing_reference_id_remains_unresolved():
    result=link_numeric_citations('[1]',{'1':{'source_sha256':'a'*64}},'a'*64)
    assert result[0]['link_status']=='UNRESOLVED' and result[0]['target_reference_id'] is None
