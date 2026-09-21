from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.models import Applicant, Base, Document, LoanApplication, User
from app.services.document_versioning import (
    calculate_file_hash,
    find_duplicate_document,
    get_active_document,
    get_next_version_number,
)


def make_application(db: Session) -> LoanApplication:
    user = User(
        email="document-versioning@example.com",
        password_hash="test",
        role="APPLICANT",
    )
    applicant = Applicant(
        full_name="Document Versioning Applicant",
        monthly_income=80000,
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


def test_sha256_is_stable_for_exact_file_bytes():
    data = b"%PDF-test-document"
    assert calculate_file_hash(data) == calculate_file_hash(data)
    assert calculate_file_hash(data) != calculate_file_hash(b"%PDF-other-document")


def test_duplicate_lookup_includes_historical_versions():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        application = make_application(db)
        file_hash = calculate_file_hash(b"document-v1")

        historical = Document(
            application_id=application.id,
            document_type="PAYSLIP",
            original_filename="old-payslip.pdf",
            storage_key="old-key",
            mime_type="application/pdf",
            file_size=100,
            file_hash=file_hash,
            is_active=False,
            version_number=1,
            status="STORED",
        )
        active = Document(
            application_id=application.id,
            document_type="PAYSLIP",
            original_filename="current-payslip.pdf",
            storage_key="current-key",
            mime_type="application/pdf",
            file_size=100,
            file_hash=calculate_file_hash(b"document-v2"),
            is_active=True,
            version_number=2,
            status="STORED",
        )
        db.add_all([historical, active])
        db.commit()

        duplicate = find_duplicate_document(
            db,
            application.id,
            "PAYSLIP",
            file_hash,
        )

        assert duplicate is not None
        assert duplicate.id == historical.id

        current = get_active_document(
            db,
            application.id,
            "PAYSLIP",
        )

        assert current is not None
        assert current.id == active.id
        assert get_next_version_number(current) == 3
        assert get_next_version_number(None) == 1
