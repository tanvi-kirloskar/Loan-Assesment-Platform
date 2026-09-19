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


def extract_bank_statement_evidence(text: str) -> dict[str, str]:
    """Extract structured fields from bank statement text."""

    evidence = {}

    patterns = {
        "account_holder_name": r"Account Holder Name:\s*(.+)",
        "salary_credit": r"Salary Credit:\s*(?:INR|₹)\s*([\d,]+)",
        "credit_date": r"Credit Date:\s*(.+)",
    }

    for field_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            evidence[field_name] = match.group(1).strip()

    return evidence

def extract_tax_return_evidence(text: str) -> dict[str, str]:
    """Extract structured fields from a synthetic tax return."""

    evidence = {}

    patterns = {
        "taxpayer_name": r"Taxpayer Name:\s*(.+)",
        "assessment_year": r"Assessment Year:\s*(.+)",
        "gross_total_income": r"Gross Total Income:\s*(?:INR|₹)\s*([\d,]+)",
        "total_tax_payable": r"Total Tax Payable:\s*(?:INR|₹)\s*([\d,]+)",
    }

    for field_name, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            evidence[field_name] = match.group(1).strip()

    return evidence