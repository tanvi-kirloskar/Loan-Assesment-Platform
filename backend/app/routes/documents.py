from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.services.verification import verify_income, verify_name
from app.models import (
    Applicant,
    Document,
    DocumentEvidence,
    LoanApplication,
    User,
    VerificationFinding,
    VerificationRun,
)
from app.schemas import (
    DocumentEvidenceResponse,
    DocumentResponse,
    DocumentRequirementResponse,
    VerificationFindingResponse,
    VerificationRunResponse,
)
from app.services.verification import (
    verify_employer,
    verify_income,
    verify_name,
)
from app.services.document_extraction import extract_pdf_text
from app.services.document_validation import MAX_FILE_SIZE, validate_document
from app.services.document_versioning import (
    calculate_file_hash,
    find_duplicate_document,
    get_active_document,
    get_next_version_number,
)
from app.services.evidence_extraction import (
    extract_bank_statement_evidence,
    extract_payslip_evidence,
    extract_tax_return_evidence,
)
from app.services.evidence_persistence import save_document_evidence
from app.services.finding_persistence import save_verification_finding
from app.services.verification_run import (
    complete_verification_run,
    fail_verification_run,
    get_latest_verification_run,
    start_verification_run,
)
from app.services.verification import (
    verify_employer,
    verify_income,
    verify_name,
    verify_payslip_tax_return_income,
    verify_salary_credit,
    verify_tax_return_income,
)
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

    file_hash = calculate_file_hash(file_data)

    duplicate = find_duplicate_document(
        db=db,
        application_id=application_id,
        document_type=document_type,
        file_hash=file_hash,
    )

    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An identical document has already been uploaded for this application.",
        )

    active_document = get_active_document(
        db=db,
        application_id=application_id,
        document_type=document_type,
    )

    next_version = get_next_version_number(active_document)

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
        file_hash=file_hash,
        is_active=True,
        version_number=next_version,
        status="UPLOADED",
    )

    db.add(document)

    try:
        storage_provider.store(
            file_data=file_data,
            storage_key=storage_key,
        )

        document.status = "STORED"

        if active_document is not None:
            active_document.is_active = False

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
    "/applications/{application_id}/document-requirements",
    response_model=list[DocumentRequirementResponse],
)
def get_document_requirements(
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

    requirements = []

    for document_type in ("PAYSLIP", "BANK_STATEMENT", "TAX_RETURN"):
        active_document = get_active_document(
            db=db,
            application_id=application_id,
            document_type=document_type,
        )

        requirements.append(
            {
                "document_type": document_type,
                "required": True,
                "satisfied": active_document is not None,
                "active_document_id": (
                    active_document.id if active_document is not None else None
                ),
                "active_version": (
                    active_document.version_number
                    if active_document is not None
                    else None
                ),
                "active_filename": (
                    active_document.original_filename
                    if active_document is not None
                    else None
                ),
            }
        )

    return requirements


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

@router.post(
    "/applications/{application_id}/documents/{document_id}/analyze",
    response_model=list[DocumentEvidenceResponse],
)
def analyze_document(
    application_id: int,
    document_id: UUID,
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

    if document.status != "STORED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is not ready for analysis.",
        )

    if document.mime_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are supported for analysis currently.",
        )

    try:
        file_data = storage_provider.retrieve(
            document.storage_key,
        )

        text = extract_pdf_text(file_data)

        if not text:
            raise ValueError("No text could be extracted from the PDF.")

        # Select the appropriate evidence extractor
        if document.document_type == "PAYSLIP":
            evidence = extract_payslip_evidence(text)

        elif document.document_type == "BANK_STATEMENT":
            evidence = extract_bank_statement_evidence(text)

        elif document.document_type == "TAX_RETURN":
            evidence = extract_tax_return_evidence(text)

        else:
            raise ValueError(
                f"Evidence extraction is not implemented for "
                f"{document.document_type} yet."
            )
        if not evidence:
            raise ValueError("No structured evidence could be extracted.")

        saved_evidence = save_document_evidence(
            db=db,
            document=document,
            evidence=evidence,
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored document file not found.",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze document.",
        )

    return saved_evidence


@router.post(
    "/applications/{application_id}/verify",
    response_model=list[VerificationFindingResponse],
)
def verify_application(
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

    payslip = (
        db.query(Document)
        .filter(
            Document.application_id == application_id,
            Document.document_type == "PAYSLIP",
        )
        .order_by(Document.created_at.desc())
        .first()
    )

    if payslip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payslip found for this application",
        )

    if payslip.status != "STORED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payslip must be analyzed before verification",
        )

    evidence_rows = (
        db.query(DocumentEvidence)
        .filter(
            DocumentEvidence.document_id == payslip.id,
        )
        .all()
    )

    evidence = {
        row.field_name: row.extracted_value
        for row in evidence_rows
    }

    findings = []

    # ---------------------------------------------------------
    # Income verification
    # ---------------------------------------------------------
    if "gross_income" in evidence:
        findings.append(
            verify_income(
                application,
                evidence["gross_income"],
            )
        )
    else:
        findings.append(
            {
                "finding_type": "GROSS_INCOME_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": (
                    "Gross income could not be extracted from the payslip."
                ),
                "action": "REVIEW",
            }
        )

    # ---------------------------------------------------------
    # Name verification
    # ---------------------------------------------------------
    if "employee_name" in evidence:
        findings.append(
            verify_name(
                application,
                evidence["employee_name"],
            )
        )
    else:
        findings.append(
            {
                "finding_type": "EMPLOYEE_NAME_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": (
                    "Employee name could not be extracted from the payslip."
                ),
                "action": "REVIEW",
            }
        )

    # ---------------------------------------------------------
    # Employer verification
    # ---------------------------------------------------------
    if "employer" in evidence:
        findings.append(
            verify_employer(
                application,
                evidence["employer"],
            )
        )
    else:
        findings.append(
            {
                "finding_type": "EMPLOYER_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": (
                    "Employer information could not be extracted from the payslip."
                ),
                "action": "REVIEW",
            }
        )

    # ---------------------------------------------------------
    # Cross-document salary verification
    # ---------------------------------------------------------
    bank_statement = (
        db.query(Document)
        .filter(
            Document.application_id == application_id,
            Document.document_type == "BANK_STATEMENT",
        )
        .order_by(Document.created_at.desc())
        .first()
    )

    if bank_statement is not None and bank_statement.status == "STORED":
        bank_evidence_rows = (
            db.query(DocumentEvidence)
            .filter(
                DocumentEvidence.document_id == bank_statement.id,
            )
            .all()
        )

        bank_evidence = {
            row.field_name: row.extracted_value
            for row in bank_evidence_rows
        }

        if "gross_income" in evidence and "salary_credit" in bank_evidence:
            findings.append(
                verify_salary_credit(
                    evidence["gross_income"],
                    bank_evidence["salary_credit"],
                )
            )
        else:
            findings.append(
                {
                    "finding_type": "SALARY_CROSS_DOCUMENT_EVIDENCE_MISSING",
                    "severity": "WARNING",
                    "message": (
                        "Salary evidence was not available in both the "
                        "payslip and bank statement for cross-document verification."
                    ),
                    "action": "REVIEW",
                }
            )
       
    # ---------------------------------------------------------
    # Tax return income verification
    # ---------------------------------------------------------

    tax_return = (
        db.query(Document)
        .filter(
            Document.application_id == application_id,
            Document.document_type == "TAX_RETURN",
        )
        .order_by(Document.created_at.desc())
        .first()
    )

    tax_return_evidence = {}

    if tax_return is not None and tax_return.status == "STORED":
        tax_return_evidence_rows = (
            db.query(DocumentEvidence)
            .filter(
                DocumentEvidence.document_id == tax_return.id,
            )
            .all()
        )

        tax_return_evidence = {
            row.field_name: row.extracted_value
            for row in tax_return_evidence_rows
        }

        if "gross_total_income" in tax_return_evidence:
            findings.append(
                verify_tax_return_income(
                    application,
                    tax_return_evidence["gross_total_income"],
                )
            )
        else:
            findings.append(
                {
                    "finding_type": "TAX_RETURN_INCOME_EVIDENCE_MISSING",
                    "severity": "WARNING",
                    "message": (
                        "Gross total income could not be extracted "
                        "from the tax return."
                    ),
                    "action": "REVIEW",
                }
            )
    # ---------------------------------------------------------
    # Payslip ↔ Tax Return income verification
    # ---------------------------------------------------------
    if (
        "gross_income" in evidence
        and "gross_total_income" in tax_return_evidence
    ):
        findings.append(
            verify_payslip_tax_return_income(
                evidence["gross_income"],
                tax_return_evidence["gross_total_income"],
            )
        )
    else:
        findings.append(
            {
                "finding_type": "PAYSLIP_TAX_RETURN_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": (
                    "Income evidence was not available in both the "
                    "payslip and tax return for cross-document verification."
                ),
                "action": "REVIEW",
            }
        )
    # ---------------------------------------------------------
    # Persist findings as one immutable verification run
    # ---------------------------------------------------------
    verification_run = start_verification_run(
        db=db,
        application_id=application_id,
    )

    saved_findings = []

    try:
        for finding in findings:
            saved_finding = save_verification_finding(
                db,
                application,
                verification_run,
                finding,
            )
            saved_findings.append(saved_finding)

        complete_verification_run(db, verification_run)
    except Exception:
        fail_verification_run(db, verification_run)
        raise

    return saved_findings


@router.get(
    "/applications/{application_id}/findings",
    response_model=list[VerificationFindingResponse],
)
def get_application_findings(
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

    latest_run = get_latest_verification_run(
        db=db,
        application_id=application_id,
    )

    if latest_run is None:
        return []

    return (
        db.query(VerificationFinding)
        .filter(
            VerificationFinding.application_id == application_id,
            VerificationFinding.run_id == latest_run.id,
        )
        .order_by(VerificationFinding.created_at.desc())
        .all()
    )


@router.get(
    "/applications/{application_id}/verification-runs",
    response_model=list[VerificationRunResponse],
)
def get_verification_runs(
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
        db.query(VerificationRun)
        .filter(VerificationRun.application_id == application_id)
        .order_by(VerificationRun.run_number.desc())
        .all()
    )


@router.get(
    "/applications/{application_id}/verification-runs/{run_id}/findings",
    response_model=list[VerificationFindingResponse],
)
def get_verification_run_findings(
    application_id: int,
    run_id: UUID,
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

    run = (
        db.query(VerificationRun)
        .filter(
            VerificationRun.id == run_id,
            VerificationRun.application_id == application_id,
        )
        .first()
    )

    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification run not found",
        )

    return (
        db.query(VerificationFinding)
        .filter(
            VerificationFinding.application_id == application_id,
            VerificationFinding.run_id == run.id,
        )
        .order_by(VerificationFinding.created_at.asc())
        .all()
    )
