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