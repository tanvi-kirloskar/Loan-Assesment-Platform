from app.services.evidence_extraction import (
    extract_bank_statement_evidence,
    extract_payslip_evidence,
    extract_tax_return_evidence,
)


def test_payslip_table_style_text_extracts_fields():
    text = """
    PAYSLIP
    Employee Name
    Aarav Mehta
    Employer
    BlueOrbit Technologies Pvt Ltd
    Gross Salary
    ₹120,000
    Net Salary
    ₹104,500
    Pay Period
    August 2026
    """

    evidence = extract_payslip_evidence(text)

    assert evidence["employee_name"] == "Aarav Mehta"
    assert evidence["employer"] == "BlueOrbit Technologies Pvt Ltd"
    assert evidence["gross_income"] == "120000"
    assert evidence["net_income"] == "104500"


def test_bank_statement_extracts_account_holder_and_salary_credit():
    text = """
    BANK STATEMENT
    Account Holder
    Aarav Mehta
    Salary Credit
    ₹104,500
    Salary Credit Date
    31-Aug-2026
    """

    evidence = extract_bank_statement_evidence(text)

    assert evidence["account_holder_name"] == "Aarav Mehta"
    assert evidence["salary_credit"] == "104500"
    assert evidence["credit_date"] == "31-Aug-2026"


def test_tax_return_supports_annual_income_label():
    text = """
    TAX RETURN
    Taxpayer Name
    Aarav Mehta
    Annual Income
    ₹1,440,000
    Financial Year
    2025-26
    """

    evidence = extract_tax_return_evidence(text)

    assert evidence["taxpayer_name"] == "Aarav Mehta"
    assert evidence["gross_total_income"] == "1440000"
    assert evidence["assessment_year"] == "2025-26"


def test_missing_values_are_not_fabricated():
    text = """
    PAYSLIP
    Employee Name
    Kabir Joshi
    Employer
    Vertex Consulting Pvt Ltd
    Gross Salary
    Net Salary
    ₹87,000
    """

    evidence = extract_payslip_evidence(text)

    assert "gross_income" not in evidence
    assert evidence["net_income"] == "87000"
