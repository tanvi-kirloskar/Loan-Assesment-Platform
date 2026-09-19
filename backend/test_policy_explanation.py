from app.services.policy_explanation import generate_policy_explanation
from app.services.policy_retriever import (
    build_policy_retriever,
    retrieve_policy,
)


def main():
    index, chunks, model = build_policy_retriever()

    query = "How should payslip and tax return income be verified?"

    policy_results = retrieve_policy(
        query,
        index,
        chunks,
        model,
        top_k=3,
    )

    evidence = [
        {
            "field": "payslip_gross_income",
            "value": "80,000",
        },
        {
            "field": "tax_return_gross_total_income",
            "value": "9,60,000",
        },
    ]

    findings = [
        {
            "finding_type": "PAYSLIP_TAX_RETURN_INCOME_MATCH",
            "severity": "INFO",
            "message": (
                "Annualized payslip gross income of ₹960,000 "
                "matches tax-return gross income of ₹960,000."
            ),
            "action": "CONTINUE",
        }
    ]

    assessment_result = {
        "decision": "APPROVED",
        "note": "Synthetic test result only.",
    }

    explanation = generate_policy_explanation(
        evidence=evidence,
        findings=findings,
        policy_chunks=policy_results,
        assessment_result=assessment_result,
    )

    print("\n=== POLICY EXPLANATION ===\n")
    print(explanation)


if __name__ == "__main__":
    main()