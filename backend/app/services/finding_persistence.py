from sqlalchemy.orm import Session

from app.models import LoanApplication, VerificationFinding


def save_verification_finding(
    db: Session,
    application: LoanApplication,
    finding: dict,
) -> VerificationFinding:
    """Persist a verification finding for a loan application."""

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