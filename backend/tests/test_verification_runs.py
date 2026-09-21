from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Applicant, Base, LoanApplication, User, VerificationFinding
from app.services.finding_persistence import save_verification_finding
from app.services.verification_run import (
    complete_verification_run,
    get_latest_verification_run,
    start_verification_run,
)


def make_application(db: Session) -> LoanApplication:
    user = User(
        email="run-history@example.com",
        password_hash="test",
        role="APPLICANT",
    )
    applicant = Applicant(
        full_name="Run History Applicant",
        monthly_income=75000,
        user=user,
    )
    application = LoanApplication(
        applicant=applicant,
        loan_amount=500000,
        loan_tenure_months=60,
        loan_purpose="HOME",
        existing_monthly_emi=0,
        credit_score=750,
        credit_score_source="MOCK",
    )
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


def test_new_verification_run_becomes_current_without_mutating_history():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        application = make_application(db)

        first_run = start_verification_run(db, application.id)
        first_finding = save_verification_finding(
            db,
            application,
            first_run,
            {
                "finding_type": "NAME_MISMATCH",
                "severity": "WARNING",
                "message": "First run finding",
                "action": "REVIEW",
            },
        )
        complete_verification_run(db, first_run)

        second_run = start_verification_run(db, application.id)
        second_finding = save_verification_finding(
            db,
            application,
            second_run,
            {
                "finding_type": "EMPLOYER_MISMATCH",
                "severity": "WARNING",
                "message": "Second run finding",
                "action": "REVIEW",
            },
        )
        complete_verification_run(db, second_run)

        db.refresh(first_finding)
        db.refresh(second_finding)

        latest = get_latest_verification_run(db, application.id)
        assert latest is not None
        assert latest.id == second_run.id
        assert latest.run_number == 2

        current_findings = (
            db.query(VerificationFinding)
            .filter(
                VerificationFinding.application_id == application.id,
                VerificationFinding.run_id == latest.id,
            )
            .all()
        )

        assert [finding.id for finding in current_findings] == [second_finding.id]

        history = (
            db.query(VerificationFinding)
            .filter(VerificationFinding.application_id == application.id)
            .order_by(VerificationFinding.created_at.asc())
            .all()
        )

        assert {finding.id for finding in history} == {
            first_finding.id,
            second_finding.id,
        }
        assert first_finding.run_id == first_run.id
        assert second_finding.run_id == second_run.id

        runs = (
            db.query(type(second_run))
            .filter(type(second_run).application_id == application.id)
            .order_by(type(second_run).run_number.asc())
            .all()
        )

        assert len(runs) == 2
        assert runs[0].is_latest is False
        assert runs[1].is_latest is True
