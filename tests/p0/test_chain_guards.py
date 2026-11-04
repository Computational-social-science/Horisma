from horisma_p0.chain_guards import single_role_support_eligibility


def test_authorship_alone_cannot_promote_naming():
    result=single_role_support_eligibility('AUTHORSHIP','LABEL_NAMING')
    assert result['disposition']=='CROSS_ROLE_INFERENCE_BLOCKED'
    assert result['scientific_approval_granted'] is False


def test_same_role_still_needs_evidence_and_scope_review():
    result=single_role_support_eligibility('LABEL_NAMING','LABEL_NAMING')
    assert result['role_comparable'] and not result['scientific_approval_granted']
