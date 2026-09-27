from sqlalchemy.orm import Session

from app.models import Document, DocumentEvidence
from app.services.document_extraction import extract_pdf_text
from app.services.evidence_extraction import (
    extract_bank_statement_evidence,
    extract_payslip_evidence,
    extract_tax_return_evidence,
)
from app.services.evidence_persistence import save_document_evidence
from app.storage.base import BaseStorageProvider


def extract_document_evidence(
    document: Document,
    file_data: bytes,
) -> dict[str, str]:
    """Extract structured evidence using the document's declared type."""

    if document.mime_type != "application/pdf":
        raise ValueError("Only PDF documents are supported for analysis currently.")

    text = extract_pdf_text(file_data)
    if not text:
        raise ValueError("No text could be extracted from the PDF.")

    if document.document_type == "PAYSLIP":
        evidence = extract_payslip_evidence(text)
    elif document.document_type == "BANK_STATEMENT":
        evidence = extract_bank_statement_evidence(text)
    elif document.document_type == "TAX_RETURN":
        evidence = extract_tax_return_evidence(text)
    else:
        raise ValueError(
            f"Evidence extraction is not implemented for {document.document_type}."
        )

    return evidence


def analyze_stored_document(
    db: Session,
    document: Document,
    storage_provider: BaseStorageProvider,
) -> list[DocumentEvidence]:
    """Retrieve a stored document, extract evidence, and persist it."""

    if document.status != "STORED":
        raise ValueError("Document is not ready for analysis.")

    file_data = storage_provider.retrieve(document.storage_key)
    evidence = extract_document_evidence(document, file_data)

    if not evidence:
        # An intentionally incomplete document can legitimately produce
        # partial/empty evidence. Verification is responsible for turning
        # missing fields into REQUEST_INFORMATION findings.
        return []

    return save_document_evidence(
        db=db,
        document=document,
        evidence=evidence,
    )
