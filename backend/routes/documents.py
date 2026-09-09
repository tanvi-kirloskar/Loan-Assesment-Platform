from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Applicant, Document, LoanApplication, User
from app.schemas import DocumentResponse
from app.services.document_validation import validate_document
from app.storage.base import BaseStorageProvider
from app.storage.provider import get_storage_provider


router = APIRouter()


ALLOWED_DOCUMENT_TYPES = {
    "PAYSLIP",
    "BANK_STATEMENT",
    "TAX_RETURN",
}


@router.post(
    "/applications/{application_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    application_id: int,
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage_provider: BaseStorageProvider = Depends(get_storage_provider),
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

    document_type = document_type.upper()

    if document_type not in ALLOWED_DOCUMENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Unsupported document type. Allowed types are "
                "PAYSLIP, BANK_STATEMENT, and TAX_RETURN."
            ),
        )

    file_data = await file.read()

    try:
        extension = validate_document(
            filename=file.filename or "",
            file_data=file_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    document_id = uuid4()

    storage_key = (
        f"applications/{application_id}/"
        f"documents/{document_id}{extension}"
    )

    document = Document(
        id=document_id,
        application_id=application_id,
        document_type=document_type,
        original_filename=file.filename or "unknown",
        storage_key=storage_key,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(file_data),
        status="UPLOADED",
    )

    db.add(document)

    try:
        storage_provider.store(
            file_data=file_data,
            storage_key=storage_key,
        )

        document.status = "STORED"

        db.commit()
        db.refresh(document)

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store document",
        )

    return document