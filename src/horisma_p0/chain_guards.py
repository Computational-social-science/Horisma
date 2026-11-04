"""Eligibility constraints, not historical verdicts or automatic approvals."""
from .operators import ContractError


def single_role_support_eligibility(evidence_role:str,target_role:str)->dict:
    if not evidence_role or not target_role:raise ContractError('EXPLICIT_ROLES_REQUIRED')
    comparable=evidence_role==target_role
    return {'role_comparable':comparable,'disposition':'REQUIRES_SCOPE_AND_EVIDENCE_REVIEW' if comparable else 'CROSS_ROLE_INFERENCE_BLOCKED',
        'scientific_approval_granted':False,'claim_truth_decided':False}
