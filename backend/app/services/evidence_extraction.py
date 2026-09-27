import re


CURRENCY_PREFIX = r"(?:INR|₹|■)?\s*"


def _lines(text: str) -> list[str]:
    """Normalize PDF text into non-empty logical lines."""

    return [
        re.sub(r"\s+", " ", line).strip()
        for line in text.replace("\r", "\n").split("\n")
        if line.strip()
    ]


def _extract_labeled_value(
    text: str,
    labels: tuple[str, ...],
) -> str | None:
    """Extract a value from either 'Label: value' or table-style PDF text.

    PDF text extraction often separates a table cell label and value onto
    adjacent lines, so relying only on colon-delimited text is brittle.
    """

    lines = _lines(text)

    for index, line in enumerate(lines):
        for label in labels:
            colon_match = re.fullmatch(
                rf"{re.escape(label)}\s*:\s*(.+)",
                line,
                flags=re.IGNORECASE,
            )
            if colon_match:
                value = colon_match.group(1).strip()
                if value:
                    return value

            if line.casefold() == label.casefold():
                if index + 1 < len(lines):
                    next_line = lines[index + 1]
                    if next_line and next_line.casefold() not in {
                        item.casefold() for item in labels
                    }:
                        return next_line

    return None


def _extract_number(value: str | None) -> str | None:
    """Return the first numeric amount from a PDF-extracted value."""

    if not value:
        return None

    match = re.search(
        rf"{CURRENCY_PREFIX}([\d,]+(?:\.\d+)?)",
        value,
        flags=re.IGNORECASE,
    )
    if not match:
        return None

    return match.group(1).replace(",", "")


def extract_payslip_evidence(text: str) -> dict[str, str]:
    """Extract structured fields from payslip text."""

    evidence: dict[str, str] = {}

    employee_name = _extract_labeled_value(text, ("Employee Name",))
    employer = _extract_labeled_value(text, ("Employer",))
    pay_period = _extract_labeled_value(text, ("Pay Period",))
    gross_income = _extract_number(
        _extract_labeled_value(text, ("Gross Salary",))
    )
    net_income = _extract_number(
        _extract_labeled_value(text, ("Net Salary",))
    )

    if employee_name:
        evidence["employee_name"] = employee_name
    if employer:
        evidence["employer"] = employer
    if pay_period:
        evidence["pay_period"] = pay_period
    if gross_income:
        evidence["gross_income"] = gross_income
    if net_income:
        evidence["net_income"] = net_income

    return evidence


def extract_bank_statement_evidence(text: str) -> dict[str, str]:
    """Extract structured fields from bank statement text."""

    evidence: dict[str, str] = {}

    account_holder_name = _extract_labeled_value(
        text,
        ("Account Holder Name", "Account Holder"),
    )
    salary_credit = _extract_number(
        _extract_labeled_value(text, ("Salary Credit",))
    )
    credit_date = _extract_labeled_value(
        text,
        ("Credit Date", "Salary Credit Date"),
    )

    if account_holder_name:
        evidence["account_holder_name"] = account_holder_name
    if salary_credit:
        evidence["salary_credit"] = salary_credit
    if credit_date:
        evidence["credit_date"] = credit_date

    return evidence


def extract_tax_return_evidence(text: str) -> dict[str, str]:
    """Extract structured fields from a synthetic tax return."""

    evidence: dict[str, str] = {}

    taxpayer_name = _extract_labeled_value(text, ("Taxpayer Name",))
    assessment_year = _extract_labeled_value(
        text,
        ("Assessment Year", "Financial Year"),
    )
    gross_total_income = _extract_number(
        _extract_labeled_value(
            text,
            ("Gross Total Income", "Annual Income"),
        )
    )
    total_tax_payable = _extract_number(
        _extract_labeled_value(text, ("Total Tax Payable",))
    )

    if taxpayer_name:
        evidence["taxpayer_name"] = taxpayer_name
    if assessment_year:
        evidence["assessment_year"] = assessment_year
    if gross_total_income:
        evidence["gross_total_income"] = gross_total_income
    if total_tax_payable:
        evidence["total_tax_payable"] = total_tax_payable

    return evidence
