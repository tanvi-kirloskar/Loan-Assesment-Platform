from app.services.loan_graph import build_loan_graph


def main():
    graph = build_loan_graph()

    initial_state = {
        "application_id": "test-application",

        "evidence": [
            {
                "field": "payslip_gross_income",
                "value": "80,000",
            },
            {
                "field": "tax_return_gross_total_income",
                "value": "9,60,000",
            },
        ],

        "findings": [
            {
                "finding_type": "PAYSLIP_TAX_RETURN_INCOME_MATCH",
                "severity": "INFO",
                "message": (
                    "Annualized payslip gross income of ₹960,000 "
                    "matches tax-return gross income of ₹960,000."
                ),
                "action": "CONTINUE",
            }
        ],

        "assessment_result": {
            "decision": "APPROVED",
            "note": "Synthetic test result only.",
        },

        "policy_query": (
            "How should payslip and tax return income be verified?"
        ),
    }

    result = graph.invoke(initial_state)

    print("\n=== GRAPH RESULT ===")
    print("Retrieved policy:", len(result["retrieved_policy"]))
    print("Review required:", result["review_required"])

    print("\n=== EXPLANATION ===")
    print(result["explanation"])


if __name__ == "__main__":
    main()