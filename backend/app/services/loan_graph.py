from langgraph.graph import END, START, StateGraph

from app.services.graph_state import LoanAssessmentState
from app.services.policy_explanation import generate_policy_explanation
from app.services.policy_retriever import (
    build_policy_retriever,
    retrieve_policy,
)


def policy_retrieval_node(
    state: LoanAssessmentState,
) -> dict:
    """Retrieve policy relevant to the current workflow."""

    index, chunks, model = build_policy_retriever()

    query = state.get(
        "policy_query",
        "What policies are relevant to this loan assessment?",
    )

    results = retrieve_policy(
        query,
        index,
        chunks,
        model,
        top_k=3,
    )

    return {
        "retrieved_policy": results,
    }


def ai_explanation_node(
    state: LoanAssessmentState,
) -> dict:
    """Generate a policy-grounded AI explanation."""

    explanation = generate_policy_explanation(
        evidence=state.get("evidence", []),
        findings=state.get("findings", []),
        policy_chunks=state.get("retrieved_policy", []),
        assessment_result=state.get("assessment_result"),
    )

    return {
        "explanation": explanation,
    }


def review_routing_node(
    state: LoanAssessmentState,
) -> dict:
    """Determine whether existing findings require human review."""

    findings = state.get("findings", [])

    review_required = any(
        finding.get("severity") in {"WARNING", "ERROR"}
        or finding.get("action") == "REVIEW"
        for finding in findings
    )

    return {
        "review_required": review_required,
    }


def build_loan_graph():
    """Build the loan assessment LangGraph workflow."""

    graph = StateGraph(LoanAssessmentState)

    graph.add_node("policy_retrieval", policy_retrieval_node)
    graph.add_node("ai_explanation", ai_explanation_node)
    graph.add_node("review_routing", review_routing_node)

    graph.add_edge(START, "policy_retrieval")
    graph.add_edge("policy_retrieval", "ai_explanation")
    graph.add_edge("ai_explanation", "review_routing")
    graph.add_edge("review_routing", END)

    return graph.compile()