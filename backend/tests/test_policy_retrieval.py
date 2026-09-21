from app.services.policy_retrieval import retrieve_policy


def test_policy_retrieval_returns_relevant_credit_policy():
    results = retrieve_policy("credit score minimum threshold")

    assert results
    assert results[0]["section"] == "Credit Score"
    assert "600" in results[0]["content"]


def test_policy_retrieval_returns_verification_policy():
    results = retrieve_policy("missing document verification finding")

    assert results
    assert results[0]["section"] == "Verification Findings"


def test_policy_retrieval_limits_results():
    results = retrieve_policy("credit score FOIR LTI verification", max_results=2)

    assert len(results) <= 2
