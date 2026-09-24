from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Applicant, Document, LoanApplication, User
from app.schemas import LoanApplicationResponse
from app.services.assessment import assess_loan
from app.services.document_validation import MAX_FILE_SIZE, validate_document
from app.services.document_versioning import calculate_file_hash
from app.storage.base import BaseStorageProvider
from app.storage.provider import get_storage_provider

router = APIRouter()

MIME_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


async def _read_required_file(file: UploadFile, label: str) -> tuple[bytes, str]:
    file_data = await file.read(MAX_FILE_SIZE + 1)

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{label} must be 5 MB or smaller.",
        )

    try:
        extension = validate_document(
            filename=file.filename or "",
            file_data=file_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{label}: {exc}",
        )

    return file_data, extension


@router.post(
    "/applications",
    response_model=LoanApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_application(
    full_name: str = Form(...),
    monthly_income: int = Form(...),
    loan_amount: int = Form(...),
    loan_tenure_months: int = Form(...),
    loan_purpose: str = Form(...),
    existing_monthly_emi: int = Form(...),
    credit_score: int = Form(...),
    credit_score_source: str = Form("MOCK"),
    payslip: UploadFile = File(...),
    bank_statement: UploadFile = File(...),
    tax_return: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage_provider: BaseStorageProvider = Depends(get_storage_provider),
):
    try:
        assessment = assess_loan(
            monthly_income=monthly_income,
            existing_monthly_emi=existing_monthly_emi,
            loan_amount=loan_amount,
            loan_tenure_months=loan_tenure_months,
            loan_purpose=loan_purpose,
            credit_score=credit_score,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    required_files = [
        ("PAYSLIP", "Payslip", payslip),
        ("BANK_STATEMENT", "Bank statement", bank_statement),
        ("TAX_RETURN", "Tax return", tax_return),
    ]

    prepared_files = []
    for document_type, label, upload in required_files:
        file_data, extension = await _read_required_file(upload, label)
        prepared_files.append(
            (document_type, label, upload, file_data, extension)
        )

    applicant = (
        db.query(Applicant)
        .filter(Applicant.user_id == current_user.id)
        .first()
    )

    if applicant is None:
        applicant = Applicant(
            full_name=full_name.strip(),
            monthly_income=monthly_income,
            age=None,
            employment_type=None,
            employer=None,
            years_employed=None,
            user_id=current_user.id,
        )
        db.add(applicant)
        db.flush()

    new_application = LoanApplication(
        applicant_id=applicant.id,
        loan_amount=loan_amount,
        loan_tenure_months=loan_tenure_months,
        loan_purpose=loan_purpose,
        existing_monthly_emi=existing_monthly_emi,
        status="submitted",
        decision=assessment["decision"],
        credit_score=credit_score,
        credit_score_source=credit_score_source,
        interest_rate=assessment["interest_rate"],
        emi=assessment["emi"],
        foir=assessment["foir"],
        lti=assessment["lti"],
        assessment_reasons="; ".join(assessment["reasons"]),
    )

    db.add(new_application)
    db.flush()

    stored_keys = []

    try:
        for document_type, label, upload, file_data, extension in prepared_files:
            document_id = uuid4()
            storage_key = (
                f"applications/{new_application.id}/"
                f"documents/{document_id}{extension}"
            )

            document = Document(
                id=document_id,
                application_id=new_application.id,
                document_type=document_type,
                original_filename=upload.filename or "unknown",
                storage_key=storage_key,
                mime_type=MIME_TYPES[extension],
                file_size=len(file_data),
                file_hash=calculate_file_hash(file_data),
                is_active=True,
                version_number=1,
                status="UPLOADED",
            )

            db.add(document)
            storage_provider.store(
                file_data=file_data,
                storage_key=storage_key,
            )
            stored_keys.append(storage_key)
            document.status = "STORED"

        db.commit()
        db.refresh(new_application)

    except Exception:
        db.rollback()

        for storage_key in stored_keys:
            try:
                storage_provider.delete(storage_key)
            except Exception:
                pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The application could not be submitted with its required documents.",
        )

    return new_application


@router.get(
    "/applications",
    response_model=list[LoanApplicationResponse],
)
def get_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    applications = (
        db.query(LoanApplication)
        .join(Applicant)
        .filter(Applicant.user_id == current_user.id)
        .order_by(LoanApplication.id.desc())
        .all()
    )

    return applications


@router.get(
    "/applications/{application_id}",
    response_model=LoanApplicationResponse,
)
def get_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = (
        db.query(LoanApplication)
        .join(Applicant)
        .filter(
            LoanApplication.id == application_id,
            Applicant.user_id == current_user.id,
        )
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application
