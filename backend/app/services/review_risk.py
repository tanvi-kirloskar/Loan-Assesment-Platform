"""Deterministic advisor review-risk scoring.

This score is a transparent workflow signal for advisor triage.
It is not a probability of default, credit score, or AI prediction, and
it never changes the D3 assessment decision.
"""

from typing import Any


D3_RISK_FACTORS = (
    ("CREDIT_SCORE_BELOW_MINIMUM", "Credit score below configured minimum", 25),
    ("FOIR_ABOVE_LIMIT", "FOIR exceeds configured limit", 25),
    ("LTI_ABOVE_LIMIT", "LTI exceeds configured limit", 25),
)

SEVERITY_POINTS = {
    "ERROR": 20,
    "WARNING": 10,
    "INFO": 0,
}


def calculate_review_risk(
    *,
    assessment: dict[str, Any],
    findings: list[dict[str, Any]] | list[Any],
) -> dict[str, Any]:
    """Return a deterministic 0-100 review-risk score and its factors."""

    score = 0
    factors: list[dict[str, Any]] = []

    credit_score = assessment.get("credit_score")
    if credit_score is not None and credit_score < 600:
        points = 25
        score += points
        factors.append({
            "code": "CREDIT_SCORE_BELOW_MINIMUM",
            "label": "Credit score below configured minimum",
            "points": points,
        })

    foir = assessment.get("foir")
    if foir is not None and float(foir) > 50:
        points = 25
        score += points
        factors.append({
            "code": "FOIR_ABOVE_LIMIT",
            "label": "FOIR exceeds configured limit",
            "points": points,
        })

    lti = assessment.get("lti")
    if lti is not None and float(lti) > 5:
        points = 25
        score += points
        factors.append({
            "code": "LTI_ABOVE_LIMIT",
            "label": "LTI exceeds configured limit",
            "points": points,
        })

    for finding in findings:
        if isinstance(finding, dict):
            severity = finding.get("severity")
            finding_type = finding.get("finding_type", "VERIFICATION_FINDING")
            message = finding.get("message", "")
        else:
            severity = getattr(finding, "severity", None)
            finding_type = getattr(finding, "finding_type", "VERIFICATION_FINDING")
            message = getattr(finding, "message", "")

        points = SEVERITY_POINTS.get(str(severity).upper(), 0)
        if points:
            score += points
            factors.append({
                "code": finding_type,
                "label": message or finding_type,
                "points": points,
            })

    return {
        "score": min(score, 100),
        "factors": factors,
    }
