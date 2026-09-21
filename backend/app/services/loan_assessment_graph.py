from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.models import Document, DocumentEvidence, LoanApplication
from app.services.assessment import assess_loan
from app.services.finding_persistence import save_verification_finding
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


REQUIRED_DOCUMENT_TYPES = ("PAYSLIP", "BANK_STATEMENT", "TAX_RETURN")


class LoanWorkflowState(TypedDict, total=False):
    db: Session
    application_id: int
    application: LoanApplication
    active_documents: dict[str, Document | None]
    evidence: dict[str, dict[str, str]]
    findings: list[dict[str, Any]]
    verification_run_id: str
    assessment: dict[str, Any]
    policy_context: list[dict[str, Any]]
    ai_explanation: str
    review_route: str


def load_application(state: LoanWorkflowState) -> dict[str, Any]:
    db = state["db"]
    application = db.query(LoanApplication).filter(
        LoanApplication.id == state["application_id"]
    ).first()

    if application is None:
        raise ValueError("Application not found.")

    active_documents: dict[str, Document | None] = {}
    evidence: dict[str, dict[str, str]] = {}

    for document_type in REQUIRED_DOCUMENT_TYPES:
        document = (
            db.query(Document)
            .filter(
                Document.application_id == application.id,
                Document.document_type == document_type,
                Document.is_active.is_(True),
            )
            .order_by(Document.created_at.desc())
            .first()
        )
        active_documents[document_type] = document
        evidence[document_type] = {}

        if document is not None and document.status == "STORED":
            rows = db.query(DocumentEvidence).filter(
                DocumentEvidence.document_id == document.id
            ).all()
            evidence[document_type] = {
                row.field_name: row.extracted_value for row in rows
            }

    return {
        "application": application,
        "active_documents": active_documents,
        "evidence": evidence,
    }


def verify_evidence(state: LoanWorkflowState) -> dict[str, Any]:
    application = state["application"]
    active_documents = state["active_documents"]
    evidence = state["evidence"]
    findings: list[dict[str, Any]] = []

    payslip = active_documents["PAYSLIP"]
    payslip_evidence = evidence["PAYSLIP"]

    if payslip is None:
        findings.append({
            "finding_type": "REQUIRED_PAYSLIP_MISSING",
            "severity": "WARNING",
            "message": "Required payslip is missing.",
            "action": "REQUEST_INFORMATION",
        })
    elif payslip.status != "STORED":
        findings.append({
            "finding_type": "PAYSLIP_NOT_READY",
            "severity": "WARNING",
            "message": "The active payslip is not ready for verification.",
            "action": "REQUEST_INFORMATION",
        })
    else:
        if "gross_income" in payslip_evidence:
            findings.append(verify_income(application, payslip_evidence["gross_income"]))
        else:
            findings.append({
                "finding_type": "GROSS_INCOME_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": "Gross income could not be extracted from the payslip.",
                "action": "REQUEST_INFORMATION",
            })

        if "employee_name" in payslip_evidence:
            findings.append(verify_name(application, payslip_evidence["employee_name"]))
        else:
            findings.append({
                "finding_type": "EMPLOYEE_NAME_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": "Employee name could not be extracted from the payslip.",
                "action": "REQUEST_INFORMATION",
            })

        if "employer" in payslip_evidence:
            findings.append(verify_employer(application, payslip_evidence["employer"]))
        else:
            findings.append({
                "finding_type": "EMPLOYER_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": "Employer information could not be extracted from the payslip.",
                "action": "REQUEST_INFORMATION",
            })

    bank_evidence = evidence["BANK_STATEMENT"]
    bank = active_documents["BANK_STATEMENT"]
    if bank is not None and bank.status == "STORED":
        if "gross_income" in payslip_evidence and "salary_credit" in bank_evidence:
            findings.append(
                verify_salary_credit(
                    payslip_evidence["gross_income"],
                    bank_evidence["salary_credit"],
                )
            )
        else:
            findings.append({
                "finding_type": "SALARY_CROSS_DOCUMENT_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": "Salary evidence was not available in both documents.",
                "action": "REQUEST_INFORMATION",
            })

    tax_evidence = evidence["TAX_RETURN"]
    tax_return = active_documents["TAX_RETURN"]
    if tax_return is not None and tax_return.status == "STORED":
        if "gross_total_income" in tax_evidence:
            findings.append(
                verify_tax_return_income(
                    application,
                    tax_evidence["gross_total_income"],
                )
            )
        else:
            findings.append({
                "finding_type": "TAX_RETURN_INCOME_EVIDENCE_MISSING",
                "severity": "WARNING",
                "message": "Gross total income could not be extracted from the tax return.",
                "action": "REQUEST_INFORMATION",
            })

    if "gross_income" in payslip_evidence and "gross_total_income" in tax_evidence:
        findings.append(
            verify_payslip_tax_return_income(
                payslip_evidence["gross_income"],
                tax_evidence["gross_total_income"],
            )
        )

    run = start_verification_run(
        db=state["db"],
        application_id=application.id,
    )

    try:
        for finding in findings:
            save_verification_finding(
                state["db"],
                application,
                run,
                finding,
            )
        complete_verification_run(state["db"], run)
    except Exception:
        fail_verification_run(state["db"], run)
        raise

    return {
        "findings": findings,
        "verification_run_id": str(run.id),
    }


def run_d3_assessment(state: LoanWorkflowState) -> dict[str, Any]:
    application = state["application"]
    assessment = assess_loan(
        monthly_income=application.applicant.monthly_income,
        existing_monthly_emi=application.existing_monthly_emi,
        loan_amount=application.loan_amount,
        loan_tenure_months=application.loan_tenure_months,
        loan_purpose=application.loan_purpose,
        credit_score=application.credit_score or 0,
    )
    return {"assessment": assessment}


def retrieve_policy(state: LoanWorkflowState) -> dict[str, Any]:
    # Phase 4 will replace this deterministic extension point with RAG.
    return {
        "policy_context": [
            {
                "source": "configured_internal_policy",
                "content": "Policy retrieval is not enabled until the RAG phase.",
            }
        ]
    }


def generate_ai_explanation(state: LoanWorkflowState) -> dict[str, Any]:
    # Phase 4 will replace this extension point with Gemini.
    assessment = state["assessment"]
    return {
        "ai_explanation": (
            f"D3 assessment decision: {assessment['decision']}. "
            "AI explanation will be generated from retrieved policy evidence in Phase 4."
        )
    }


def route_for_review(state: LoanWorkflowState) -> dict[str, Any]:
    findings = state["findings"]
    assessment = state["assessment"]

    if any(
        finding["action"] == "REQUEST_INFORMATION"
        for finding in findings
    ):
        route = "REQUEST_INFORMATION"
    elif any(
        finding["finding_type"] in {
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
        for finding in findings
    ):
        route = "HUMAN_REVIEW"
    else:
        # A D3 rejection remains deterministic; it does not become a
        # human-review decision automatically.
        route = "CONTINUE"

    return {"review_route": route}


def build_loan_assessment_graph():
    graph = StateGraph(LoanWorkflowState)

    graph.add_node("load_application", load_application)
    graph.add_node("verification", verify_evidence)
    graph.add_node("d3_assessment", run_d3_assessment)
    graph.add_node("policy_retrieval", retrieve_policy)
    graph.add_node("ai_explanation", generate_ai_explanation)
    graph.add_node("review_routing", route_for_review)

    graph.add_edge(START, "load_application")
    graph.add_edge("load_application", "verification")
    graph.add_edge("verification", "d3_assessment")
    graph.add_edge("d3_assessment", "policy_retrieval")
    graph.add_edge("policy_retrieval", "ai_explanation")
    graph.add_edge("ai_explanation", "review_routing")
    graph.add_edge("review_routing", END)

    return graph.compile()


loan_assessment_graph = build_loan_assessment_graph()
