from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
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
    VerificationRun,
    AuditLog,
)
from app.services.review_risk import calculate_review_risk
from app.services.assessment import MAX_FOIR, MAX_LTI, MIN_CREDIT_SCORE
from app.workflows.loan_assessment import build_advisor_workflow_summary, route_from_findings
from app.storage.base import BaseStorageProvider
from app.storage.provider import get_storage_provider
from app.schemas import (
    AdvisorApplicationDetailResponse,
    AdvisorApplicationSummaryResponse,
    AdvisorDocumentResponse,
    AdvisorEvidenceResponse,
    AdvisorFindingResponse,
    AdvisorDecisionRequest,
    AdvisorAuditLogResponse,
    AdvisorWorkflowResponse,
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

    results = []
    for application in applications:
        latest_run = (
            db.query(VerificationRun)
            .filter(
                VerificationRun.application_id == application.id,
                VerificationRun.is_latest.is_(True),
            )
            .first()
        )
        findings = []
        if latest_run is not None:
            findings = (
                db.query(VerificationFinding)
                .filter(
                    VerificationFinding.application_id == application.id,
                    VerificationFinding.run_id == latest_run.id,
                )
                .all()
            )

        review_risk = calculate_review_risk(
            assessment={
                "credit_score": application.credit_score,
                "foir": application.foir,
                "lti": application.lti,
            },
            findings=findings,
        )

        results.append({
            "id": application.id,
            "applicant_id": application.applicant_id,
            "applicant_name": application.applicant.full_name,
            "loan_amount": application.loan_amount,
            "status": application.status,
            "decision": application.decision,
            "assessment_decision": application.assessment_decision,
            "foir": application.foir,
            "lti": application.lti,
            "review_risk_score": review_risk["score"],
        })

    return results


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

    latest_run = (
        db.query(VerificationRun)
        .filter(
            VerificationRun.application_id == application_id,
            VerificationRun.is_latest.is_(True),
        )
        .first()
    )

    verification_history = (
        db.query(VerificationRun)
        .filter(VerificationRun.application_id == application_id)
        .order_by(VerificationRun.run_number.desc())
        .all()
    )

    latest_findings = []
    if latest_run is not None:
        latest_findings = (
            db.query(VerificationFinding)
            .filter(
                VerificationFinding.application_id == application_id,
                VerificationFinding.run_id == latest_run.id,
            )
            .order_by(VerificationFinding.created_at.asc())
            .all()
        )

    assessment = {
        "credit_score": application.credit_score or 0,
        "foir": application.foir,
        "lti": application.lti,
    }
    review_risk = calculate_review_risk(
        assessment=assessment,
        findings=latest_findings,
    )
    finding_dicts = [
        {
            "finding_type": finding.finding_type,
            "action": finding.action,
        }
        for finding in latest_findings
    ]
    workflow_route = route_from_findings(finding_dicts)

    return {
        "id": application.id,
        "applicant_id": application.applicant_id,
        "applicant_name": application.applicant.full_name,
        "loan_amount": application.loan_amount,
        "loan_tenure_months": application.loan_tenure_months,
        "loan_purpose": application.loan_purpose,
        "monthly_income": application.applicant.monthly_income,
        "existing_monthly_emi": application.existing_monthly_emi,
        "status": application.status,
        "decision": application.decision,
        "assessment_decision": application.assessment_decision,
        "credit_score": application.credit_score,
        "credit_score_source": application.credit_score_source,
        "interest_rate": application.interest_rate,
        "emi": application.emi,
        "foir": application.foir,
        "lti": application.lti,
        "review_risk_score": review_risk["score"],
        "review_risk_factors": review_risk["factors"],
        "assessment_reasons": application.assessment_reasons,
        "decision_reasons": (
            application.assessment_reasons.split("; ")
            if application.assessment_reasons
            else []
        ),
        "verification_route": workflow_route,
        "verification_run": latest_run,
        "verification_history": verification_history,
        "documents": documents,
        "evidence": evidence,
        "findings": latest_findings,
    }


@router.get(
    "/applications/{application_id}/documents/{document_id}/view",
)
def view_advisor_document(
    application_id: int,
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    storage_provider: BaseStorageProvider = Depends(get_storage_provider),
):
    require_role(current_user, "ADVISOR")
    _get_advisor_application(application_id, db)

    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.application_id == application_id,
            Document.is_active.is_(True),
            Document.status == "STORED",
        )
        .first()
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active submitted document not found",
        )

    try:
        file_data = storage_provider.retrieve(document.storage_key)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stored document file not found.",
        )

    safe_filename = (document.original_filename or "document").replace('"', "")
    return Response(
        content=file_data,
        media_type=document.mime_type,
        headers={
            "Content-Disposition": f'inline; filename="{safe_filename}"',
            "Cache-Control": "private, no-store",
        },
    )


@router.get(
    "/applications/{application_id}/workflow",
    response_model=AdvisorWorkflowResponse,
)
def get_advisor_workflow(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, "ADVISOR")
    application = _get_advisor_application(application_id, db)

    workflow_summary = build_advisor_workflow_summary(
        db=db,
        application_id=application_id,
    )

    return workflow_summary


ALLOWED_ADVISOR_ACTIONS = {
    "APPROVE": "approved",
    "REJECT": "rejected",
    "REQUEST_INFO": "information_requested",
}


@router.get(
    "/applications/{application_id}/audit",
    response_model=list[AdvisorAuditLogResponse],
)
def get_advisor_audit_log(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, "ADVISOR")
    _get_advisor_application(application_id, db)

    return (
        db.query(AuditLog)
        .filter(AuditLog.application_id == application_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )


@router.post(
    "/applications/{application_id}/decision",
    response_model=AdvisorAuditLogResponse,
)
def submit_advisor_decision(
    application_id: int,
    payload: AdvisorDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, "ADVISOR")
    application = _get_advisor_application(application_id, db)

    action = payload.action.upper()
    if action not in ALLOWED_ADVISOR_ACTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid advisor action.",
        )

    if not payload.notes or not payload.notes.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decision rationale is required.",
        )

    if application.status in {"approved", "rejected"}:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A final advisor decision has already been recorded for this application.",
        )

    previous_status = application.status
    new_status = ALLOWED_ADVISOR_ACTIONS[action]

    application.status = new_status
    application.decision = (
        "APPROVED" if action == "APPROVE"
        else "REJECTED" if action == "REJECT"
        else None
    )

    audit = AuditLog(
        application_id=application.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        action=action,
        previous_status=previous_status,
        new_status=new_status,
        notes=payload.notes.strip(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


@router.post(
    "/applications/{application_id}/request-info",
    response_model=AdvisorAuditLogResponse,
)
def request_application_information(
    application_id: int,
    payload: AdvisorDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_role(current_user, "ADVISOR")
    application = _get_advisor_application(application_id, db)

    if not payload.notes or not payload.notes.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Information request details are required.",
        )

    previous_status = application.status
    application.status = "information_requested"
    application.decision = None

    audit = AuditLog(
        application_id=application.id,
        actor_id=current_user.id,
        actor_role=current_user.role,
        action="REQUEST_INFO",
        previous_status=previous_status,
        new_status=application.status,
        notes=payload.notes.strip(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit
