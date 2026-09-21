import hashlib

from sqlalchemy.orm import Session

from app.models import Document


def calculate_file_hash(file_data: bytes) -> str:
    """Return the SHA-256 digest for uploaded file bytes."""
    return hashlib.sha256(file_data).hexdigest()


def find_duplicate_document(
    db: Session,
    application_id: int,
    document_type: str,
    file_hash: str,
) -> Document | None:
    """Find an exact byte-for-byte duplicate, including historical versions."""
    return (
        db.query(Document)
        .filter(
            Document.application_id == application_id,
            Document.document_type == document_type,
            Document.file_hash == file_hash,
        )
        .first()
    )


def get_active_document(
    db: Session,
    application_id: int,
    document_type: str,
) -> Document | None:
    """Return the current active version for one document requirement."""
    return (
        db.query(Document)
        .filter(
            Document.application_id == application_id,
            Document.document_type == document_type,
            Document.is_active.is_(True),
        )
        .first()
    )


def get_next_version_number(active_document: Document | None) -> int:
    """Calculate the next version for a document requirement."""
    if active_document is None:
        return 1
    return active_document.version_number + 1
