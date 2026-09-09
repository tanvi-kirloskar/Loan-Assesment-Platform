from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Applicant, Document, LoanApplication, User
from app.schemas import DocumentResponse
from app.services.document_validation import MAX_FILE_SIZE, validate_document
from app.storage.base import BaseStorageProvider
from app.storage.provider import get_storage_provider


router = APIRouter()


ALLOWED_DOCUMENT_TYPES = {
    "PAYSLIP",
    "BANK_STATEMENT",
    "TAX_RETURN",
}


MIME_TYPES = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
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

    file_data = await file.read(MAX_FILE_SIZE + 1)

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

    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5 MB limit.",
        )

    document_id = uuid4()

    storage_key = (
        f"applications/{application_id}/"
        f"documents/{document_id}{extension}"
    )

    mime_type = MIME_TYPES[extension]

    document = Document(
        id=document_id,
        application_id=application_id,
        document_type=document_type,
        original_filename=file.filename or "unknown",
        storage_key=storage_key,
        mime_type=mime_type,
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

        try:
            storage_provider.delete(storage_key)
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store document",
        )

    return document


@router.get(
    "/applications/{application_id}/documents",
    response_model=list[DocumentResponse],
)
def list_documents(
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

    return (
        db.query(Document)
        .filter(Document.application_id == application_id)
        .order_by(Document.created_at.desc())
        .all()
    )


@router.get(
    "/applications/{application_id}/documents/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    application_id: int,
    document_id: UUID,
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

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.application_id == application_id,
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    return document