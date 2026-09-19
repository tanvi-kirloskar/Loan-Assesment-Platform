from app.services.loan_graph import ai_explanation_node


def main():
    state = {
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
                    "Annualized payslip gross income of "
                    "₹960,000 matches tax-return gross income "
                    "of ₹960,000."
                ),
                "action": "CONTINUE",
            }
        ],
        "retrieved_policy": [
            {
                "section": "5. Payslip and Tax Return Consistency",
                "content": (
                    "Monthly payslip gross income may be annualized "
                    "using Monthly Gross Income × 12 and compared "
                    "with tax-return gross income."
                ),
            }
        ],
        "assessment_result": {
            "decision": "APPROVED",
            "note": "Synthetic test result only.",
        },
    }

    result = ai_explanation_node(state)

    print("\n=== ADVISORY NODE TEST ===")
    print(result["explanation"])


if __name__ == "__main__":
    main()