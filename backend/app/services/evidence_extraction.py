import re


def extract_payslip_evidence(text: str) -> dict[str, str]:
    """Extract structured fields from payslip text."""

    evidence = {}

    patterns = {
        "employee_name": r"Employee Name:\s*(.+)",
        "employer": r"Employer:\s*(.+)",
        "pay_period": r"Pay Period:\s*(.+)",
        "gross_income": r"Gross Salary:\s*(?:INR|₹)\s*([\d,]+)",
        "net_income": r"Net Salary:\s*(?:INR|₹)\s*([\d,]+)",
    }

    for field_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            evidence[field_name] = match.group(1).strip()

    return evidence