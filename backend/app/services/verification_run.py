from datetime import datetime, timezone

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import VerificationRun


def start_verification_run(db: Session, application_id: int) -> VerificationRun:
    """Create a new historical verification run without changing the current run yet."""

    max_run_number = (
        db.query(func.max(VerificationRun.run_number))
        .filter(VerificationRun.application_id == application_id)
        .scalar()
    )

    run = VerificationRun(
        application_id=application_id,
        run_number=(max_run_number or 0) + 1,
        status="RUNNING",
        is_latest=False,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def complete_verification_run(db: Session, run: VerificationRun) -> VerificationRun:
    """Mark a run complete and make it the application's current run."""

    db.query(VerificationRun).filter(
        VerificationRun.application_id == run.application_id,
        VerificationRun.is_latest.is_(True),
    ).update({"is_latest": False}, synchronize_session=False)

    run.status = "COMPLETED"
    run.is_latest = True
    run.completed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(run)
    return run


def fail_verification_run(db: Session, run: VerificationRun) -> VerificationRun:
    """Record a failed execution while leaving the previous latest run unchanged."""

    run.status = "FAILED"
    run.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(run)
    return run


def get_latest_verification_run(
    db: Session,
    application_id: int,
) -> VerificationRun | None:
    return (
        db.query(VerificationRun)
        .filter(
            VerificationRun.application_id == application_id,
            VerificationRun.is_latest.is_(True),
        )
        .first()
    )
