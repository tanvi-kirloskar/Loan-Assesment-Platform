from sqlalchemy.orm import Session

from app.models import Document, DocumentEvidence


def save_document_evidence(
    db: Session,
    document: Document,
    evidence: dict[str, str],
) -> list[DocumentEvidence]:
    """Persist extracted evidence for a document."""

    saved_evidence = []

    for field_name, extracted_value in evidence.items():
        item = DocumentEvidence(
            document_id=document.id,
            field_name=field_name,
            extracted_value=extracted_value,
        )

        db.add(item)
        saved_evidence.append(item)

    db.commit()

    for item in saved_evidence:
        db.refresh(item)

    return saved_evidence