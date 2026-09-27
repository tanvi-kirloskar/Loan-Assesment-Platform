from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.models import (
    Applicant,
    Document,
    DocumentEvidence,
    LoanApplication,
    VerificationFinding,
    VerificationRun,
)
from app.services.ai_explanation import generate_ai_explanation
from app.services.assessment import MAX_FOIR, MAX_LTI, MIN_CREDIT_SCORE
from app.services.finding_persistence import save_verification_finding
from app.services.policy_retrieval import retrieve_policy
from app.services.review_risk import calculate_review_risk
from app.services.verification import (
    verify_employer,
    verify_income,
    verify_name,
    verify_payslip_tax_return_income,
    verify_salary_credit,
    verify_tax_return_income,
)
from app.services.verification_run import (
    complete_verification_run,
    fail_verification_run,
    start_verification_run,
)


class LoanWorkflowState(TypedDict, total=False):
    application_id: int
    application: LoanApplication
    evidence: dict[str, dict[str, str]]
    findings: list[dict[str, str]]
    verification_run: VerificationRun | None
    route: str
    policy_evidence: list[dict[str, str]]
    ai_explanation: dict[str, str]
    review_risk: dict[str, Any]


HUMAN_REVIEW_FINDING_TYPES = {
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
    "GROSS_INCOME_EVIDENCE_MISSING",
    "EMPLOYEE_NAME_EVIDENCE_MISSING",
    "EMPLOYER_EVIDENCE_MISSING",
    "SALARY_CROSS_DOCUMENT_EVIDENCE_MISSING",
    "TAX_RETURN_INCOME_EVIDENCE_MISSING",
    "PAYSLIP_TAX_RETURN_EVIDENCE_MISSING",
}


def _application_or_raise(
    db: Session,
    application_id: int,
) -> LoanApplication:
    application = (
        db.query(LoanApplication)
        .join(Applicant)
        .filter(LoanApplication.id == application_id)
        .first()
    )
    if application is None:
        raise ValueError("Application not found.")
    return application


def _latest_active_document(
    db: Session,
    application_id: int,
    document_type: str,
) -> Document | None:
    return (
        db.query(Document)
        .filter(
            Document.application_id == application_id,
            Document.document_type == document_type,
            Document.is_active.is_(True),
        )
        .order_by(Document.created_at.desc())
        .first()
    )


def _document_evidence(
    db: Session,
    document: Document | None,
) -> dict[str, str]:
    if document is None:
        return {}

    rows = (
        db.query(DocumentEvidence)
        .filter(DocumentEvidence.document_id == document.id)
        .all()
    )
    return {row.field_name: row.extracted_value for row in rows}


def _missing_finding(
    finding_type: str,
    message: str,
) -> dict[str, str]:
    return {
        "finding_type": finding_type,
        "severity": "WARNING",
        "message": message,
        "action": "REQUEST_INFORMATION",
    }


def _build_findings(
    application: LoanApplication,
    evidence: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    payslip = evidence["PAYSLIP"]
    bank = evidence["BANK_STATEMENT"]
    tax = evidence["TAX_RETURN"]
    findings: list[dict[str, str]] = []

    if "gross_income" in payslip:
        findings.append(verify_income(application, payslip["gross_income"]))
    else:
        findings.append(_missing_finding(
            "GROSS_INCOME_EVIDENCE_MISSING",
            "Gross income could not be extracted from the payslip.",
        ))

    if "employee_name" in payslip:
        findings.append(verify_name(application, payslip["employee_name"]))
    else:
        findings.append(_missing_finding(
            "EMPLOYEE_NAME_EVIDENCE_MISSING",
            "Employee name could not be extracted from the payslip.",
        ))

    if "employer" in payslip:
        findings.append(verify_employer(application, payslip["employer"]))
    else:
        findings.append(_missing_finding(
            "EMPLOYER_EVIDENCE_MISSING",
            "Employer information could not be extracted from the payslip.",
        ))

    if "gross_income" in payslip and "salary_credit" in bank:
        findings.append(
            verify_salary_credit(
                payslip["gross_income"],
                bank["salary_credit"],
            )
        )
    else:
        findings.append(_missing_finding(
            "SALARY_CROSS_DOCUMENT_EVIDENCE_MISSING",
            "Salary evidence was not available in both the payslip and bank statement for cross-document verification.",
        ))

    if "gross_total_income" in tax:
        findings.append(
            verify_tax_return_income(
                application,
                tax["gross_total_income"],
            )
        )
    else:
        findings.append(_missing_finding(
            "TAX_RETURN_INCOME_EVIDENCE_MISSING",
            "Gross total income could not be extracted from the tax return.",
        ))

    if "gross_income" in payslip and "gross_total_income" in tax:
        findings.append(
            verify_payslip_tax_return_income(
                payslip["gross_income"],
                tax["gross_total_income"],
            )
        )
    else:
        findings.append(_missing_finding(
            "PAYSLIP_TAX_RETURN_EVIDENCE_MISSING",
            "Income evidence was not available in both the payslip and tax return for cross-document verification.",
        ))

    return findings


def route_from_findings(findings: list[dict[str, str]]) -> str:
    """Determine workflow routing without allowing the LLM to make the decision."""
    if any(item.get("action") == "REQUEST_INFORMATION" for item in findings):
        return "REQUEST_INFORMATION"

    if any(
        item.get("action") == "REVIEW"
        or item.get("finding_type") in HUMAN_REVIEW_FINDING_TYPES
        for item in findings
    ):
        return "HUMAN_REVIEW"

    return "CONTINUE"


def _assessment_dict(application: LoanApplication) -> dict[str, Any]:
    return {
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
        "interest_rate": (
            float(application.interest_rate)
            if application.interest_rate is not None
            else None
        ),
        "emi": float(application.emi) if application.emi is not None else None,
        "minimum_credit_score": MIN_CREDIT_SCORE,
        "maximum_foir": MAX_FOIR,
        "maximum_lti": MAX_LTI,
    }


def build_advisor_workflow_summary(
    db: Session,
    application_id: int,
) -> dict[str, Any]:
    """Build the advisor-facing workflow summary from the latest persisted run.

    This does not execute verification or mutate the database. The POST
    /verify endpoint is the single entry point that runs the LangGraph.
    """
    application = _application_or_raise(db, application_id)

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

    finding_dicts = [
        {
            "finding_type": finding.finding_type,
            "severity": finding.severity,
            "message": finding.message,
            "action": finding.action,
        }
        for finding in findings
    ]

    route = route_from_findings(finding_dicts)
    review_risk = calculate_review_risk(
        assessment=_assessment_dict(application),
        findings=findings,
    )

    policy_evidence = retrieve_policy(
        " ".join([
            "loan assessment policy",
            str(application.decision or ""),
            application.assessment_reasons or "",
            " ".join(item["finding_type"] for item in finding_dicts),
        ]),
        max_results=3,
    )

    ai_explanation = generate_ai_explanation(
        assessment=_assessment_dict(application),
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

def build_loan_workflow(db: Session):
    """Build the application verification -> RAG -> advisory LangGraph.

    The graph orchestrates deterministic services. The LLM is used only for
    grounded explanation after verification and policy retrieval.
    """

    def load_context(state: LoanWorkflowState) -> dict[str, Any]:
        application = _application_or_raise(db, state["application_id"])

        payslip = _latest_active_document(db, application.id, "PAYSLIP")
        if payslip is None:
            raise ValueError("No payslip found for this application.")
        if payslip.status != "STORED":
            raise ValueError("Payslip must be stored before verification.")

        evidence = {
            "PAYSLIP": _document_evidence(db, payslip),
            "BANK_STATEMENT": _document_evidence(
                db,
                _latest_active_document(db, application.id, "BANK_STATEMENT"),
            ),
            "TAX_RETURN": _document_evidence(
                db,
                _latest_active_document(db, application.id, "TAX_RETURN"),
            ),
        }
        return {
            "application": application,
            "evidence": evidence,
        }

    def verify_documents(state: LoanWorkflowState) -> dict[str, Any]:
        return {
            "findings": _build_findings(
                state["application"],
                state["evidence"],
            )
        }

    def persist_findings(state: LoanWorkflowState) -> dict[str, Any]:
        run = start_verification_run(db, state["application_id"])
        try:
            for finding in state["findings"]:
                save_verification_finding(
                    db,
                    state["application"],
                    run,
                    finding,
                )
            complete_verification_run(db, run)
        except Exception:
            fail_verification_run(db, run)
            raise

        return {"verification_run": run}

    def route_workflow(state: LoanWorkflowState) -> dict[str, Any]:
        route = route_from_findings(state["findings"])
        review_risk = calculate_review_risk(
            assessment=_assessment_dict(state["application"]),
            findings=state["findings"],
        )
        return {
            "route": route,
            "review_risk": review_risk,
        }

    def retrieve_policy_node(state: LoanWorkflowState) -> dict[str, Any]:
        application = state["application"]
        query = " ".join([
            "loan assessment policy",
            str(application.decision or ""),
            application.assessment_reasons or "",
            " ".join(
                item["finding_type"]
                for item in state["findings"]
            ),
        ])
        return {
            "policy_evidence": retrieve_policy(
                query,
                max_results=3,
            )
        }

    def advisory_node(state: LoanWorkflowState) -> dict[str, Any]:
        assessment = _assessment_dict(state["application"])
        explanation = generate_ai_explanation(
            assessment=assessment,
            findings=state["findings"],
            policy_context=state["policy_evidence"],
        )
        return {"ai_explanation": explanation}

    graph = StateGraph(LoanWorkflowState)
    graph.add_node("load_context", load_context)
    graph.add_node("verify_documents", verify_documents)
    graph.add_node("persist_findings", persist_findings)
    graph.add_node("route_workflow", route_workflow)
    graph.add_node("retrieve_policy", retrieve_policy_node)
    graph.add_node("advisory", advisory_node)

    graph.add_edge(START, "load_context")
    graph.add_edge("load_context", "verify_documents")
    graph.add_edge("verify_documents", "persist_findings")
    graph.add_edge("persist_findings", "route_workflow")
    graph.add_edge("route_workflow", "retrieve_policy")
    graph.add_edge("retrieve_policy", "advisory")
    graph.add_edge("advisory", END)

    return graph.compile()
