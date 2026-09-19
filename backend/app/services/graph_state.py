from typing import Any, TypedDict


class LoanAssessmentState(TypedDict, total=False):
    application_id: str

    documents: list[dict[str, Any]]

    evidence: list[dict[str, Any]]

    findings: list[dict[str, Any]]

    assessment_result: dict[str, Any]

    policy_query: str

    retrieved_policy: list[dict[str, Any]]

    explanation: str

    review_required: bool