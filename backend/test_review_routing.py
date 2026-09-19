from app.services.loan_graph import review_routing_node


def test_info_finding():
    state = {
        "findings": [
            {
                "finding_type": "PAYSLIP_TAX_RETURN_INCOME_MATCH",
                "severity": "INFO",
                "action": "CONTINUE",
            }
        ]
    }

    result = review_routing_node(state)

    print("INFO finding:")
    print("Review required:", result["review_required"])


def test_warning_finding():
    state = {
        "findings": [
            {
                "finding_type": "NAME_MISMATCH",
                "severity": "WARNING",
                "action": "REVIEW",
            }
        ]
    }

    result = review_routing_node(state)

    print("\nWARNING finding:")
    print("Review required:", result["review_required"])


if __name__ == "__main__":
    test_info_finding()
    test_warning_finding()