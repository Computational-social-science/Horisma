"""Conservative eligibility for versioned automated review, never human approval."""
POLICY = "horisma-auto-review-0.1.0"
REQUIRED = ("source_identity", "processing_rights", "transcription_fidelity", "passage_support", "scope_and_modality", "dependency_freshness", "qualified_heterogeneous_review")

def decide(checks: dict, *, attempts: int = 0, max_attempts: int = 2) -> dict:
    if type(attempts) is not int or type(max_attempts) is not int or attempts < 0 or max_attempts < 1:
        raise ValueError("INVALID_RETRY_BUDGET")
    if set(checks) != set(REQUIRED) or any(type(v) is not bool for v in checks.values()):
        raise ValueError("EXPLICIT_BOOLEAN_GATES_REQUIRED")
    unmet = [key for key in REQUIRED if checks[key] is not True]
    status = "AUTO_REVIEW_ACCEPTED" if not unmet else ("ABSTAINED" if attempts >= max_attempts else "NEEDS_EVIDENCE")
    return {"policy": POLICY, "status": status, "unmet_gates": unmet,
            "human_review_performed": False, "public_release_authorized": False,
            "historical_truth_guaranteed": False}
