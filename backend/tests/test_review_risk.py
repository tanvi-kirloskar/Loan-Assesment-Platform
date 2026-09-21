from app.services.review_risk import calculate_review_risk


def test_review_risk_scores_d3_threshold_breaches():
    result = calculate_review_risk(
        assessment={"credit_score": 550, "foir": 55, "lti": 6},
        findings=[],
    )

    assert result["score"] == 75
    assert [factor["code"] for factor in result["factors"]] == [
        "CREDIT_SCORE_BELOW_MINIMUM",
        "FOIR_ABOVE_LIMIT",
        "LTI_ABOVE_LIMIT",
    ]


def test_review_risk_adds_verification_severity_points():
    result = calculate_review_risk(
        assessment={"credit_score": 750, "foir": 30, "lti": 2},
        findings=[
            {
                "finding_type": "NAME_MISMATCH",
                "severity": "WARNING",
                "message": "Names differ.",
            },
            {
                "finding_type": "INCOME_VERIFICATION_ERROR",
                "severity": "ERROR",
                "message": "Could not compare income.",
            },
            {
                "finding_type": "INCOME_MATCH",
                "severity": "INFO",
                "message": "Income matches.",
            },
        ],
    )

    assert result["score"] == 30
    assert [factor["points"] for factor in result["factors"]] == [10, 20]


def test_review_risk_is_capped_at_100():
    findings = [
        {"finding_type": f"FINDING_{i}", "severity": "ERROR", "message": "error"}
        for i in range(6)
    ]

    result = calculate_review_risk(
        assessment={"credit_score": 500, "foir": 60, "lti": 7},
        findings=findings,
    )

    assert result["score"] == 100


def test_clean_application_has_zero_review_risk():
    result = calculate_review_risk(
        assessment={"credit_score": 780, "foir": 35, "lti": 2},
        findings=[{"finding_type": "NAME_MATCH", "severity": "INFO"}],
    )

    assert result == {"score": 0, "factors": []}
