from sqlalchemy.orm import Session

from app.models import LoanApplication, VerificationFinding


def save_verification_finding(
    db: Session,
    application: LoanApplication,
    finding: dict,
) -> VerificationFinding:
    """Create or update a verification finding for an application."""

    existing_finding = (
        db.query(VerificationFinding)
        .filter(
            VerificationFinding.application_id == application.id,
            VerificationFinding.finding_type == finding["finding_type"],
        )
        .first()
    )

    if existing_finding:
        existing_finding.severity = finding["severity"]
        existing_finding.message = finding["message"]
        existing_finding.action = finding["action"]

        db.commit()
        db.refresh(existing_finding)

        return existing_finding

    verification_finding = VerificationFinding(
        application_id=application.id,
        finding_type=finding["finding_type"],
        severity=finding["severity"],
        message=finding["message"],
        action=finding["action"],
    )

    db.add(verification_finding)
    db.commit()
    db.refresh(verification_finding)

    return verification_finding