from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_role
from app.database import get_db
from app.models import (
    Applicant,
    Document,
    DocumentEvidence,
    LoanApplication,
    User,
    VerificationFinding,
)
from app.schemas import (
    AdvisorApplicationDetailResponse,
    AdvisorApplicationSummaryResponse,
    AdvisorDocumentResponse,
    AdvisorEvidenceResponse,
    AdvisorFindingResponse,
)


router = APIRouter(
    prefix="/advisor",
    tags=["advisor"],
)


def _get_advisor_application(
    application_id: int,
    db: Session,
) -> LoanApplication:
    application = (
        db.query(LoanApplication)
        .join(Applicant)
        .filter(LoanApplication.id == application_id)
        .first()
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    return application


@router.get(
    "/applications",
    response_model=list[AdvisorApplicationSummaryResponse],
)
def get_advisor_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, "ADVISOR")

    applications = (
        db.query(LoanApplication)
        .join(Applicant)
        .order_by(LoanApplication.id.desc())
        .all()
    )

    return [
        {
            "id": application.id,
            "applicant_id": application.applicant_id,
            "applicant_name": application.applicant.full_name,
            "loan_amount": application.loan_amount,
            "status": application.status,
            "decision": application.decision,
            "foir": application.foir,
            "lti": application.lti,
        }
        for application in applications
    ]


@router.get(
    "/applications/{application_id}",
    response_model=AdvisorApplicationDetailResponse,
)
def get_advisor_application(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, "ADVISOR")

    application = _get_advisor_application(application_id, db)

    documents = (
        db.query(Document)
        .filter(Document.application_id == application_id)
        .order_by(Document.created_at.desc())
        .all()
    )

    evidence = (
        db.query(DocumentEvidence)
        .join(Document)
        .filter(Document.application_id == application_id)
        .order_by(DocumentEvidence.created_at.asc())
        .all()
    )

    latest_findings = (
        db.query(VerificationFinding)
        .filter(
            VerificationFinding.application_id == application_id,
            VerificationFinding.run_id.in_(
                [
                    run.id
                    for run in application.verification_runs
                    if run.is_latest
                ]
            ),
        )
        .order_by(VerificationFinding.created_at.asc())
        .all()
    )

    return {
        "id": application.id,
        "applicant_id": application.applicant_id,
        "applicant_name": application.applicant.full_name,
        "loan_amount": application.loan_amount,
        "loan_tenure_months": application.loan_tenure_months,
        "loan_purpose": application.loan_purpose,
        "existing_monthly_emi": application.existing_monthly_emi,
        "status": application.status,
        "decision": application.decision,
        "credit_score": application.credit_score,
        "credit_score_source": application.credit_score_source,
        "interest_rate": application.interest_rate,
        "emi": application.emi,
        "foir": application.foir,
        "lti": application.lti,
        "assessment_reasons": application.assessment_reasons,
        "documents": documents,
        "evidence": evidence,
        "findings": latest_findings,
    )
