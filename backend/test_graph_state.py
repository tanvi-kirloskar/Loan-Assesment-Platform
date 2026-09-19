from app.services.graph_state import LoanAssessmentState


def main():
    state: LoanAssessmentState = {
        "application_id": "test-application",

        "findings": [
            {
                "finding_type": "PAYSLIP_TAX_RETURN_INCOME_MATCH",
                "severity": "INFO",
                "action": "CONTINUE",
            }
        ],

        "assessment_result": {
            "decision": "APPROVED",
        },

        "review_required": False,
    }

    print("LangGraph state created successfully.")
    print("Application:", state["application_id"])
    print("Findings:", len(state["findings"]))
    print("Decision:", state["assessment_result"]["decision"])
    print("Review required:", state["review_required"])


if __name__ == "__main__":
    main()