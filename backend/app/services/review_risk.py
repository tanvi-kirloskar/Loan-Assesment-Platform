"""Deterministic advisor review-risk scoring.

The score is a transparent 0-100 triage signal: higher means more
financial or verification concern. It is not a probability of default,
credit score, or AI prediction, and it never changes the rule-based
assessment decision.

Weights:
- Credit score: 30
- FOIR: 30
- LTI: 20
- Verification findings: 20
"""

from typing import Any


SEVERITY_POINTS = {
    "ERROR": 20,
    "WARNING": 10,
    "INFO": 0,
}


def _add_factor(factors: list[dict[str, Any]], code: str, label: str, points: int) -> int:
    if points <= 0:
        return 0
    factors.append({"code": code, "label": label, "points": points})
    return points


def calculate_review_risk(
    *,
    assessment: dict[str, Any],
    findings: list[dict[str, Any]] | list[Any],
) -> dict[str, Any]:
    """Return a deterministic 0-100 review-risk score and its factors."""

    score = 0
    factors: list[dict[str, Any]] = []

    credit_score = assessment.get("credit_score")
    if credit_score is not None:
        credit_score = float(credit_score)
        if credit_score < 600:
            points = 30
        elif credit_score < 650:
            points = 20
        elif credit_score < 700:
            points = 10
        elif credit_score < 750:
            points = 5
        else:
            points = 0
        score += _add_factor(
            factors,
            "CREDIT_SCORE_RISK",
            f"Credit score {int(credit_score)} falls in a higher-risk band",
            points,
        )

    foir = assessment.get("foir")
    if foir is not None:
        foir = float(foir)
        if foir > 50:
            points = 30
        elif foir > 45:
            points = 20
        elif foir > 40:
            points = 10
        else:
            points = 0
        score += _add_factor(
            factors,
            "FOIR_RISK",
            f"FOIR of {foir:.1f}% indicates elevated repayment burden",
            points,
        )

    lti = assessment.get("lti")
    if lti is not None:
        lti = float(lti)
        if lti > 5:
            points = 20
        elif lti > 4:
            points = 12
        elif lti > 3:
            points = 6
        else:
            points = 0
        score += _add_factor(
            factors,
            "LTI_RISK",
            f"LTI of {lti:.2f} indicates elevated loan-to-income exposure",
            points,
        )

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
