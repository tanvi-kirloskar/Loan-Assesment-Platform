import os

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import create_access_token, hash_password
from app.database import get_db
from app.main import app
from app.models import Applicant, Base, LoanApplication, User
from sqlalchemy.pool import StaticPool


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def seed_users_and_application():
    db = TestingSessionLocal()

    import uuid
    suffix = uuid.uuid4().hex

    applicant_user = User(
        email=f"api-applicant-{suffix}@example.com",
        password_hash=hash_password("password123"),
        role="APPLICANT",
    )
    advisor_user = User(
        email=f"api-advisor-{suffix}@example.com",
        password_hash=hash_password("password123"),
        role="ADVISOR",
    )
    db.add_all([applicant_user, advisor_user])
    db.flush()

    applicant = Applicant(
        user_id=applicant_user.id,
        full_name="API Test Applicant",
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

    application_id = application.id
    applicant_id = applicant_user.id
    advisor_id = advisor_user.id
    db.close()

    return applicant_id, advisor_id, application_id


def test_applicant_cannot_access_advisor_application_list():
    applicant_id, _, _ = seed_users_and_application()
    token = create_access_token({"sub": str(applicant_id), "role": "APPLICANT"})

    response = client.get(
        "/advisor/applications",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_advisor_can_access_application_list():
    _, advisor_id, application_id = seed_users_and_application()
    token = create_access_token({"sub": str(advisor_id), "role": "ADVISOR"})

    response = client.get(
        "/advisor/applications",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert any(item["id"] == application_id for item in response.json())


def test_applicant_cannot_access_advisor_application_detail():
    applicant_id, _, application_id = seed_users_and_application()
    token = create_access_token({"sub": str(applicant_id), "role": "APPLICANT"})

    response = client.get(
        f"/advisor/applications/{application_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_advisor_can_access_application_detail():
    _, advisor_id, application_id = seed_users_and_application()
    token = create_access_token({"sub": str(advisor_id), "role": "ADVISOR"})

    response = client.get(
        f"/advisor/applications/{application_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == application_id
    assert body["applicant_name"] == "API Test Applicant"


def test_advisor_gets_404_for_unknown_application():
    _, advisor_id, _ = seed_users_and_application()
    token = create_access_token({"sub": str(advisor_id), "role": "ADVISOR"})

    response = client.get(
        "/advisor/applications/999999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
