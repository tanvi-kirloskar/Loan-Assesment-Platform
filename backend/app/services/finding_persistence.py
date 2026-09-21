from sqlalchemy.orm import Session

from app.models import LoanApplication, VerificationFinding, VerificationRun


def save_verification_finding(
    db: Session,
    application: LoanApplication,
    verification_run: VerificationRun,
    finding: dict,
) -> VerificationFinding:
    """Persist an immutable finding produced by one verification run."""

    verification_finding = VerificationFinding(
        application_id=application.id,
        run_id=verification_run.id,
        finding_type=finding["finding_type"],
        severity=finding["severity"],
        message=finding["message"],
        action=finding["action"],
    )

    db.add(verification_finding)
    db.commit()
    db.refresh(verification_finding)

    return verification_finding
