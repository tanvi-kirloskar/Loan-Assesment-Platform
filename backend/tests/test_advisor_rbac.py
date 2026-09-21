import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.auth import require_role
from app.models import Applicant, Base, LoanApplication, User


def make_user(db: Session, role: str) -> User:
    user = User(
        email=f"{role.lower()}@example.com",
        password_hash="test",
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_advisor_role_is_allowed():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        advisor = make_user(db, "ADVISOR")

        assert require_role(advisor, "ADVISOR") is advisor


def test_applicant_role_is_forbidden_from_advisor_dependency():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        applicant = make_user(db, "APPLICANT")

        with pytest.raises(HTTPException) as exc_info:
            require_role(applicant, "ADVISOR")

        assert exc_info.value.status_code == 403


def test_advisor_can_access_application_data_model():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        advisor = make_user(db, "ADVISOR")
        applicant_user = make_user(db, "APPLICANT")
        applicant = Applicant(
            user_id=applicant_user.id,
            full_name="Advisor Review Applicant",
            monthly_income=75000,
        )
        db.add(applicant)
        db.flush()

        application = LoanApplication(
            applicant_id=applicant.id,
            loan_amount=500000,
            loan_tenure_months=60,
            loan_purpose="HOME",
            existing_monthly_emi=0,
            status="submitted",
            decision="APPROVED",
            credit_score=750,
            credit_score_source="MOCK",
        )
        db.add(application)
        db.commit()

        assert advisor.role == "ADVISOR"
        assert application.applicant.full_name == "Advisor Review Applicant"
