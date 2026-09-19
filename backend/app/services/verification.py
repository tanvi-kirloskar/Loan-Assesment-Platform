from decimal import Decimal, InvalidOperation

from app.models import LoanApplication


def verify_income(
    application: LoanApplication,
    extracted_income: str,
) -> dict:
    """Compare declared application income with payslip gross income."""

    try:
        declared_income = Decimal(str(application.applicant.monthly_income))
        document_income = Decimal(
            extracted_income.replace(",", "").strip()
        )
    except (InvalidOperation, AttributeError):
        return {
            "finding_type": "INCOME_VERIFICATION_ERROR",
            "severity": "ERROR",
            "message": "Unable to compare application income with payslip income.",
            "action": "REVIEW",
        }

    if declared_income == document_income:
        return {
            "finding_type": "INCOME_MATCH",
            "severity": "INFO",
            "message": (
                f"Declared monthly income of ₹{declared_income:,.0f} "
                f"matches payslip gross income of ₹{document_income:,.0f}."
            ),
            "action": "CONTINUE",
        }

    difference = document_income - declared_income

    return {
        "finding_type": "INCOME_MISMATCH",
        "severity": "WARNING",
        "message": (
            f"Declared monthly income of ₹{declared_income:,.0f} "
            f"differs from payslip gross income of "
            f"₹{document_income:,.0f} by ₹{abs(difference):,.0f}."
        ),
        "action": "REVIEW",
    }


def verify_name(
    application: LoanApplication,
    extracted_name: str,
) -> dict:
    """Compare applicant name with the employee name extracted from a payslip."""

    application_name = application.applicant.full_name.strip()
    document_name = extracted_name.strip()

    if application_name.casefold() == document_name.casefold():
        return {
            "finding_type": "NAME_MATCH",
            "severity": "INFO",
            "message": (
                f"Applicant name '{application_name}' "
                f"matches payslip employee name '{document_name}'."
            ),
            "action": "CONTINUE",
        }

    return {
        "finding_type": "NAME_MISMATCH",
        "severity": "WARNING",
        "message": (
            f"Applicant name '{application_name}' "
            f"does not match payslip employee name '{document_name}'."
        ),
        "action": "REVIEW",
    }
def verify_employer(
    application: LoanApplication,
    extracted_employer: str,
) -> dict:
    """Compare applicant employer with employer extracted from a payslip."""

    application_employer = application.applicant.employer
    document_employer = extracted_employer.strip()

    if not application_employer:
        return {
            "finding_type": "EMPLOYER_DATA_UNAVAILABLE",
            "severity": "INFO",
            "message": (
                "Employer information is not available in the application, "
                "so employer consistency could not be verified."
            ),
            "action": "REVIEW",
        }

    application_employer = application_employer.strip()

    if application_employer.casefold() == document_employer.casefold():
        return {
            "finding_type": "EMPLOYER_MATCH",
            "severity": "INFO",
            "message": (
                f"Application employer '{application_employer}' "
                f"matches payslip employer '{document_employer}'."
            ),
            "action": "CONTINUE",
        }

    return {
        "finding_type": "EMPLOYER_MISMATCH",
        "severity": "WARNING",
        "message": (
            f"Application employer '{application_employer}' "
            f"does not match payslip employer '{document_employer}'."
        ),
        "action": "REVIEW",
    }
def verify_salary_credit(
    payslip_income: str,
    bank_salary_credit: str,
) -> dict:
    """Compare payslip gross income with bank statement salary credit."""

    try:
        payslip_amount = Decimal(
            payslip_income.replace(",", "").strip()
        )
        bank_amount = Decimal(
            bank_salary_credit.replace(",", "").strip()
        )
    except (InvalidOperation, AttributeError):
        return {
            "finding_type": "SALARY_CROSS_DOCUMENT_VERIFICATION_ERROR",
            "severity": "ERROR",
            "message": (
                "Unable to compare payslip income with bank statement "
                "salary credit."
            ),
            "action": "REVIEW",
        }

    if payslip_amount == bank_amount:
        return {
            "finding_type": "SALARY_CROSS_DOCUMENT_MATCH",
            "severity": "INFO",
            "message": (
                f"Payslip gross income of ₹{payslip_amount:,.0f} "
                f"matches bank statement salary credit of "
                f"₹{bank_amount:,.0f}."
            ),
            "action": "CONTINUE",
        }

    difference = bank_amount - payslip_amount

    return {
        "finding_type": "SALARY_CROSS_DOCUMENT_MISMATCH",
        "severity": "WARNING",
        "message": (
            f"Payslip gross income of ₹{payslip_amount:,.0f} "
            f"differs from bank statement salary credit of "
            f"₹{bank_amount:,.0f} by ₹{abs(difference):,.0f}."
        ),
        "action": "REVIEW",
    }

def verify_tax_return_income(
    application: LoanApplication,
    tax_return_income: str,
) -> dict:
    """Compare annualized application income with tax-return gross income."""

    try:
        monthly_income = Decimal(
            str(application.applicant.monthly_income)
        )

        declared_annual_income = monthly_income * Decimal("12")

        tax_return_annual_income = Decimal(
            tax_return_income.replace(",", "").strip()
        )

    except (InvalidOperation, AttributeError):
        return {
            "finding_type": "TAX_RETURN_INCOME_VERIFICATION_ERROR",
            "severity": "ERROR",
            "message": (
                "Unable to compare application income with "
                "tax-return gross income."
            ),
            "action": "REVIEW",
        }

    if declared_annual_income == tax_return_annual_income:
        return {
            "finding_type": "TAX_RETURN_INCOME_MATCH",
            "severity": "INFO",
            "message": (
                f"Annualized declared income of "
                f"₹{declared_annual_income:,.0f} "
                f"matches tax-return gross income of "
                f"₹{tax_return_annual_income:,.0f}."
            ),
            "action": "CONTINUE",
        }

    difference = tax_return_annual_income - declared_annual_income

    return {
        "finding_type": "TAX_RETURN_INCOME_MISMATCH",
        "severity": "WARNING",
        "message": (
            f"Annualized declared income of "
            f"₹{declared_annual_income:,.0f} "
            f"differs from tax-return gross income of "
            f"₹{tax_return_annual_income:,.0f} "
            f"by ₹{abs(difference):,.0f}."
        ),
        "action": "REVIEW",
    }
def verify_payslip_tax_return_income(
    payslip_income: str,
    tax_return_income: str,
) -> dict:
    """Compare annualized payslip gross income with tax-return income."""

    try:
        monthly_payslip_income = Decimal(
            payslip_income.replace(",", "").strip()
        )

        annualized_payslip_income = (
            monthly_payslip_income * Decimal("12")
        )

        tax_return_annual_income = Decimal(
            tax_return_income.replace(",", "").strip()
        )

    except (InvalidOperation, AttributeError):
        return {
            "finding_type": "PAYSLIP_TAX_RETURN_VERIFICATION_ERROR",
            "severity": "ERROR",
            "message": (
                "Unable to compare payslip income with "
                "tax-return gross income."
            ),
            "action": "REVIEW",
        }

    if annualized_payslip_income == tax_return_annual_income:
        return {
            "finding_type": "PAYSLIP_TAX_RETURN_INCOME_MATCH",
            "severity": "INFO",
            "message": (
                f"Annualized payslip gross income of "
                f"₹{annualized_payslip_income:,.0f} "
                f"matches tax-return gross income of "
                f"₹{tax_return_annual_income:,.0f}."
            ),
            "action": "CONTINUE",
        }

    difference = (
        tax_return_annual_income - annualized_payslip_income
    )

    return {
        "finding_type": "PAYSLIP_TAX_RETURN_INCOME_MISMATCH",
        "severity": "WARNING",
        "message": (
            f"Annualized payslip gross income of "
            f"₹{annualized_payslip_income:,.0f} "
            f"differs from tax-return gross income of "
            f"₹{tax_return_annual_income:,.0f} "
            f"by ₹{abs(difference):,.0f}."
        ),
        "action": "REVIEW",
    }