"""Edge-scoped receipt binding and explicit inference counterexample guards."""
from .live_ledger import encoded
from .operators import digest
from .claim_edges import validate_claim_edge
from .receipt_verifier import verify_bundle
from .automated_review import REQUIRED
from pathlib import Path


def review_context(edge):
    return {'policy':edge['qualification']['policy'],'edge_id':edge['id'],
            'adapter_sha256':digest(Path(__file__).read_bytes()),
            'edge_sha256':digest(encoded(edge)), 'claim_sha256':edge['claim']['sha256'],
            'source_revision':edge['source']['revision'],'source_sha256':edge['source']['sha256'],
            'passage_sha256':edge['passage']['sha256'],'record_revision':edge['passage']['record_revision'],
            'relation':edge['relation']}


def review_edge(root,edge,view,bundle=None):
    validate_claim_edge(edge,view)
    context=review_context(edge)
    if bundle is None:
        bundle={'context':context,'receipts':{},'attempts':0}
    if encoded(bundle['context'])!=encoded(context):
        raise ValueError('RECEIPTS_FOR_DIFFERENT_EDGE_CONTEXT')
    result=verify_bundle(root,bundle)
    return {'context':context,'receipt_validation':result,'workflow_status':'ABSTAINED',
            'reason':'MISSING_OR_INVALID_RECEIPTS' if not all(result['checks'].values()) else 'SEMANTIC_RECEIPT_PRODUCER_AUTHENTICATION_NOT_IMPLEMENTED',
            'scientific_acceptance':False,'human_review_required':False}


def inference_guard(evidence_kind,target_kind,evidence_role,target_role):
    kinds={'BIBLIOGRAPHIC_REFERENCE','SCHEDULE','OCCURRENCE','AUTHORSHIP_ACKNOWLEDGMENT','NAMING','PASSAGE_REPORT','UNVERIFIED_REPORT','HISTORICAL_FACT'}
    roles={'AUTHORSHIP','LABEL_NAMING','MATERIAL_CONTRIBUTION','CONCEPT_DEVELOPMENT','NONE'}
    if evidence_kind not in kinds or target_kind not in kinds or evidence_role not in roles or target_role not in roles:
        raise ValueError('UNKNOWN_INFERENCE_TYPE')
    blocked=(evidence_kind=='BIBLIOGRAPHIC_REFERENCE' and target_kind=='HISTORICAL_FACT') or (evidence_kind=='SCHEDULE' and target_kind in {'OCCURRENCE','NAMING'}) or (evidence_kind=='AUTHORSHIP_ACKNOWLEDGMENT' and target_role=='LABEL_NAMING') or (evidence_kind=='UNVERIFIED_REPORT' and target_kind=='HISTORICAL_FACT')
    return {'status':'BLOCKED_INFERENCE' if blocked else 'REQUIRES_ADDITIONAL_SEMANTIC_REVIEW',
            'scientific_acceptance':False}
