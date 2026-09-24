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
from app.services.policy_retrieval import retrieve_policy
from app.services.ai_explanation import generate_ai_explanation
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

    assessment = {
        "decision": application.decision,
        "reasons": (
            application.assessment_reasons.split("; ")
            if application.assessment_reasons
            else []
        ),
        "monthly_income": application.applicant.monthly_income,
        "existing_monthly_emi": application.existing_monthly_emi,
        "loan_amount": application.loan_amount,
        "loan_tenure_months": application.loan_tenure_months,
        "loan_purpose": application.loan_purpose,
        "credit_score": application.credit_score,
        "foir": application.foir,
        "lti": application.lti,
        "interest_rate": float(application.interest_rate) if application.interest_rate is not None else None,
        "emi": float(application.emi) if application.emi is not None else None,
        "minimum_credit_score": MIN_CREDIT_SCORE,
        "maximum_foir": MAX_FOIR,
        "maximum_lti": MAX_LTI,
    }

    finding_dicts = [
        {
            "finding_type": finding.finding_type,
            "severity": finding.severity,
            "message": finding.message,
            "action": finding.action,
        }
        for finding in latest_findings
    ]
    review_risk = calculate_review_risk(
        assessment=assessment,
        findings=latest_findings,
    )
    workflow_route = "CONTINUE"
    if any(f["action"] == "REQUEST_INFORMATION" for f in finding_dicts):
        workflow_route = "REQUEST_INFORMATION"
    elif any(
        f["finding_type"] in {
            "NAME_MISMATCH",
            "EMPLOYER_MISMATCH",
            "INCOME_MISMATCH",
            "SALARY_CROSS_DOCUMENT_MISMATCH",
            "TAX_RETURN_INCOME_MISMATCH",
            "PAYSLIP_TAX_RETURN_INCOME_MISMATCH",
            "INCOME_VERIFICATION_ERROR",
            "SALARY_CROSS_DOCUMENT_VERIFICATION_ERROR",
            "TAX_RETURN_INCOME_VERIFICATION_ERROR",
            "PAYSLIP_TAX_RETURN_VERIFICATION_ERROR",
        }
        for f in finding_dicts
    ):
        workflow_route = "HUMAN_REVIEW"

    policy_evidence = retrieve_policy(
        " ".join([
            "loan assessment policy",
            str(application.decision or ""),
            application.assessment_reasons or "",
            " ".join(f["finding_type"] for f in finding_dicts),
        ]),
        max_results=3,
    )
    ai_explanation = generate_ai_explanation(
        assessment=assessment,
        findings=finding_dicts,
        policy_context=policy_evidence,
    )

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
        "credit_score": application.credit_score,
        "credit_score_source": application.credit_score_source,
        "interest_rate": application.interest_rate,
        "emi": application.emi,
        "foir": application.foir,
        "lti": application.lti,
        "review_risk_score": review_risk["score"],
        "review_risk_factors": review_risk["factors"],
        "assessment_reasons": application.assessment_reasons,
        "decision_reasons": assessment["reasons"],
        "verification_route": workflow_route,
        "verification_run": latest_run,
        "verification_history": verification_history,
        "documents": documents,
        "evidence": evidence,
        "findings": latest_findings,
        "review_risk_score": review_risk["score"],
        "review_risk_factors": review_risk["factors"],
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

    latest_run = (
        db.query(VerificationRun)
        .filter(
            VerificationRun.application_id == application_id,
            VerificationRun.is_latest.is_(True),
        )
        .first()
    )
    findings = []
    if latest_run is not None:
        findings = (
            db.query(VerificationFinding)
            .filter(
                VerificationFinding.application_id == application_id,
                VerificationFinding.run_id == latest_run.id,
            )
            .order_by(VerificationFinding.created_at.asc())
            .all()
        )

    assessment = {
        "decision": application.decision,
        "reasons": (
            application.assessment_reasons.split("; ")
            if application.assessment_reasons
            else []
        ),
        "monthly_income": application.applicant.monthly_income,
        "existing_monthly_emi": application.existing_monthly_emi,
        "loan_amount": application.loan_amount,
        "loan_tenure_months": application.loan_tenure_months,
        "loan_purpose": application.loan_purpose,
        "credit_score": application.credit_score,
        "foir": application.foir,
        "lti": application.lti,
        "interest_rate": float(application.interest_rate) if application.interest_rate is not None else None,
        "emi": float(application.emi) if application.emi is not None else None,
        "minimum_credit_score": MIN_CREDIT_SCORE,
        "maximum_foir": MAX_FOIR,
        "maximum_lti": MAX_LTI,
    }
    finding_dicts = [
        {
            "finding_type": finding.finding_type,
            "severity": finding.severity,
            "message": finding.message,
            "action": finding.action,
        }
        for finding in findings
    ]

    review_risk = calculate_review_risk(
        assessment=assessment,
        findings=findings,
    )

    if any(f["action"] == "REQUEST_INFORMATION" for f in finding_dicts):
        route = "REQUEST_INFORMATION"
    elif any(
        f["finding_type"] in {
            "NAME_MISMATCH",
            "EMPLOYER_MISMATCH",
            "INCOME_MISMATCH",
            "SALARY_CROSS_DOCUMENT_MISMATCH",
            "TAX_RETURN_INCOME_MISMATCH",
            "PAYSLIP_TAX_RETURN_INCOME_MISMATCH",
            "INCOME_VERIFICATION_ERROR",
            "SALARY_CROSS_DOCUMENT_VERIFICATION_ERROR",
            "TAX_RETURN_INCOME_VERIFICATION_ERROR",
            "PAYSLIP_TAX_RETURN_VERIFICATION_ERROR",
        }
        for f in finding_dicts
    ):
        route = "HUMAN_REVIEW"
    else:
        route = "CONTINUE"

    policy_evidence = retrieve_policy(
        " ".join([
            "loan assessment policy",
            str(application.decision or ""),
            application.assessment_reasons or "",
            " ".join(f["finding_type"] for f in finding_dicts),
        ]),
        max_results=3,
    )
    ai_explanation = generate_ai_explanation(
        assessment=assessment,
        findings=finding_dicts,
        policy_context=policy_evidence,
    )

    return {
        "route": route,
        "verification_run": latest_run,
        "policy_evidence": policy_evidence,
        "ai_explanation": ai_explanation,
        "review_risk_score": review_risk["score"],
        "review_risk_factors": review_risk["factors"],
    }


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
