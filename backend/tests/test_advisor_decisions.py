import os
import uuid

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models import Applicant, AuditLog, Base, LoanApplication, User


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)


def override_get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def seed():
    db = SessionLocal()
    suffix = uuid.uuid4().hex

    applicant_user = User(
        email=f"decision-applicant-{suffix}@example.com",
        password_hash=hash_password("password123"),
        role="APPLICANT",
    )
    advisor = User(
        email=f"decision-advisor-{suffix}@example.com",
        password_hash=hash_password("password123"),
        role="ADVISOR",
    )
    db.add_all([applicant_user, advisor])
    db.flush()

    applicant = Applicant(
        user_id=applicant_user.id,
        full_name="Decision Test Applicant",
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
    )
    db.add(application)
    db.commit()

    result = (advisor.id, applicant_user.id, application.id)
    db.close()
    return result


def token(user_id, role):
    return create_access_token({"sub": str(user_id), "role": role})


def test_advisor_approve_requires_rationale():
    advisor_id, _, application_id = seed()

    response = client.post(
        f"/advisor/applications/{application_id}/decision",
        headers={"Authorization": f"Bearer {token(advisor_id, 'ADVISOR')}"},
        json={"action": "APPROVE"},
    )

    assert response.status_code == 400


def test_applicant_cannot_submit_advisor_decision():
    _, applicant_id, application_id = seed()

    response = client.post(
        f"/advisor/applications/{application_id}/decision",
        headers={"Authorization": f"Bearer {token(applicant_id, 'APPLICANT')}"},
        json={"action": "APPROVE", "notes": "Review completed."},
    )

    assert response.status_code == 403


def test_advisor_approve_updates_application_and_creates_audit():
    advisor_id, _, application_id = seed()

    response = client.post(
        f"/advisor/applications/{application_id}/decision",
        headers={"Authorization": f"Bearer {token(advisor_id, 'ADVISOR')}"},
        json={"action": "APPROVE", "notes": "Documents reviewed and decision recorded."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "APPROVE"
    assert body["previous_status"] == "submitted"
    assert body["new_status"] == "approved"
    assert body["notes"] == "Documents reviewed and decision recorded."

    db = SessionLocal()
    application = db.get(LoanApplication, application_id)
    logs = db.query(AuditLog).filter(AuditLog.application_id == application_id).all()
    assert application.status == "approved"
    assert application.decision == "APPROVED"
    assert len(logs) == 1
    db.close()


def test_advisor_request_info_creates_audit():
    advisor_id, _, application_id = seed()

    response = client.post(
        f"/advisor/applications/{application_id}/request-info",
        headers={"Authorization": f"Bearer {token(advisor_id, 'ADVISOR')}"},
        json={"action": "REQUEST_INFO", "notes": "Please upload the latest bank statement."},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["action"] == "REQUEST_INFO"
    assert body["new_status"] == "information_requested"


def test_invalid_advisor_action_is_rejected():
    advisor_id, _, application_id = seed()

    response = client.post(
        f"/advisor/applications/{application_id}/decision",
        headers={"Authorization": f"Bearer {token(advisor_id, 'ADVISOR')}"},
        json={"action": "MAYBE", "notes": "Invalid action test."},
    )

    assert response.status_code == 400


def test_advisor_can_read_audit_history():
    advisor_id, _, application_id = seed()

    client.post(
        f"/advisor/applications/{application_id}/decision",
        headers={"Authorization": f"Bearer {token(advisor_id, 'ADVISOR')}"},
        json={"action": "REJECT", "notes": "Required evidence was not satisfactory."},
    )

    response = client.get(
        f"/advisor/applications/{application_id}/audit",
        headers={"Authorization": f"Bearer {token(advisor_id, 'ADVISOR')}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["action"] == "REJECT"
