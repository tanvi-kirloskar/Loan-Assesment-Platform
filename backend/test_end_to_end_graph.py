from app.services.loan_graph import build_loan_graph


def main():
    graph = build_loan_graph()

    initial_state = {
        "application_id": "e2e-test-001",

        "evidence": [
            {
                "field": "payslip_employee_name",
                "value": "Tanvi Sharma",
            },
            {
                "field": "application_full_name",
                "value": "Tanvi Kirloskar",
            },
            {
                "field": "payslip_gross_income",
                "value": "80,000",
            },
        ],

        "findings": [
            {
                "finding_type": "NAME_MISMATCH",
                "severity": "WARNING",
                "message": (
                    "Applicant name does not match the name "
                    "found on the payslip."
                ),
                "action": "REVIEW",
            }
        ],

        "assessment_result": {
            "decision": "APPROVED",
            "note": "Synthetic deterministic assessment result only.",
        },

        "policy_query": (
            "How should applicant identity mismatches "
            "be handled during loan verification?"
        ),
    }

    result = graph.invoke(initial_state)

    print("\n==============================")
    print("D6.32 END-TO-END GRAPH TEST")
    print("==============================")

    print("\nApplication:")
    print(result["application_id"])

    print("\nRetrieved Policy:")
    for chunk in result["retrieved_policy"]:
        print(f"- {chunk['section']}")

    print("\nReview Required:")
    print(result["review_required"])

    print("\nAI Advisory:")
    print(result["explanation"])

    print("\n==============================")
    print("END-TO-END TEST COMPLETE")
    print("==============================")


if __name__ == "__main__":
    main()