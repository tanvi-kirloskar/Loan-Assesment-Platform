from decimal import Decimal

from app.services.loan_assessment_graph import (
    LoanWorkflowState,
    build_loan_assessment_graph,
    route_for_review,
)


def test_graph_has_expected_workflow_shape():
    graph = build_loan_assessment_graph()

    assert graph is not None


def test_review_routing_requests_missing_information():
    state: LoanWorkflowState = {
        "findings": [
            {
                "finding_type": "REQUIRED_PAYSLIP_MISSING",
                "severity": "WARNING",
                "message": "Required payslip is missing.",
                "action": "REQUEST_INFORMATION",
            }
        ],
        "assessment": {"decision": "APPROVED"},
    }

    assert route_for_review(state)["review_route"] == "REQUEST_INFORMATION"


def test_review_routing_sends_identity_mismatch_to_human_review():
    state: LoanWorkflowState = {
        "findings": [
            {
                "finding_type": "NAME_MISMATCH",
                "severity": "WARNING",
                "message": "Names do not match.",
                "action": "REVIEW",
            }
        ],
        "assessment": {"decision": "APPROVED"},
    }

    assert route_for_review(state)["review_route"] == "HUMAN_REVIEW"


def test_d3_rejection_does_not_automatically_route_to_human_review():
    state: LoanWorkflowState = {
        "findings": [],
        "assessment": {
            "decision": "REJECTED",
            "reasons": ["FOIR exceeds configured threshold."],
            "foir": Decimal("60.00"),
        },
    }

    assert route_for_review(state)["review_route"] == "CONTINUE"


def test_review_routing_requests_missing_required_bank_statement():
    state: LoanWorkflowState = {
        "findings": [
            {
                "finding_type": "REQUIRED_BANK_STATEMENT_MISSING",
                "severity": "WARNING",
                "message": "Required bank statement is missing.",
                "action": "REQUEST_INFORMATION",
            }
        ],
        "assessment": {"decision": "APPROVED"},
    }

    assert route_for_review(state)["review_route"] == "REQUEST_INFORMATION"


def test_review_routing_requests_missing_required_tax_return():
    state: LoanWorkflowState = {
        "findings": [
            {
                "finding_type": "REQUIRED_TAX_RETURN_MISSING",
                "severity": "WARNING",
                "message": "Required tax return is missing.",
                "action": "REQUEST_INFORMATION",
            }
        ],
        "assessment": {"decision": "APPROVED"},
    }

    assert route_for_review(state)["review_route"] == "REQUEST_INFORMATION"
