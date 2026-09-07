from decimal import Decimal

import pytest

from app.services.assessment import assess_loan


def test_normal_loan_assessment():
    result = assess_loan(
        monthly_income=80000,
        existing_monthly_emi=10000,
        loan_amount=500000,
        loan_tenure_months=60,
        loan_purpose="PERSONAL",
        credit_score=742,
    )

    assert result["decision"] == "APPROVED"
    assert result["interest_rate"] == Decimal("0.09")
    assert result["emi"] == Decimal("10379.18")
    assert result["foir"] == Decimal("25.47")
    assert result["lti"] == Decimal("0.52")
    assert result["reasons"] == []


def test_credit_score_below_minimum_is_rejected():
    result = assess_loan(
        monthly_income=80000,
        existing_monthly_emi=10000,
        loan_amount=500000,
        loan_tenure_months=60,
        loan_purpose="PERSONAL",
        credit_score=599,
    )

    assert result["decision"] == "REJECTED"
    assert "Credit score is below configured minimum." in result["reasons"]


def test_credit_score_exactly_minimum_is_allowed():
    result = assess_loan(
        monthly_income=80000,
        existing_monthly_emi=10000,
        loan_amount=500000,
        loan_tenure_months=60,
        loan_purpose="PERSONAL",
        credit_score=600,
    )

    assert result["decision"] == "APPROVED"


def test_foir_above_threshold_is_rejected():
    result = assess_loan(
        monthly_income=30000,
        existing_monthly_emi=10000,
        loan_amount=1000000,
        loan_tenure_months=12,
        loan_purpose="PERSONAL",
        credit_score=750,
    )

    assert result["decision"] == "REJECTED"
    assert result["foir"] > Decimal("50.00")
    assert "FOIR exceeds configured threshold." in result["reasons"]


def test_lti_above_threshold_is_rejected():
    result = assess_loan(
        monthly_income=20000,
        existing_monthly_emi=0,
        loan_amount=1500000,
        loan_tenure_months=60,
        loan_purpose="HOME",
        credit_score=750,
    )

    assert result["decision"] == "REJECTED"
    assert result["lti"] > Decimal("5.00")
    assert "LTI exceeds configured threshold." in result["reasons"]


@pytest.mark.parametrize(
    "monthly_income, loan_amount, tenure, expected_message",
    [
        (0, 500000, 60, "Monthly income must be greater than zero."),
        (-1000, 500000, 60, "Monthly income must be greater than zero."),
    ],
)
def test_invalid_income(
    monthly_income,
    loan_amount,
    tenure,
    expected_message,
):
    with pytest.raises(ValueError, match=expected_message):
        assess_loan(
            monthly_income=monthly_income,
            existing_monthly_emi=0,
            loan_amount=loan_amount,
            loan_tenure_months=tenure,
            loan_purpose="PERSONAL",
            credit_score=750,
        )


def test_negative_existing_emi_is_invalid():
    with pytest.raises(
        ValueError,
        match="Existing monthly EMI cannot be negative.",
    ):
        assess_loan(
            monthly_income=80000,
            existing_monthly_emi=-1,
            loan_amount=500000,
            loan_tenure_months=60,
            loan_purpose="PERSONAL",
            credit_score=750,
        )


def test_invalid_loan_amount():
    with pytest.raises(
        ValueError,
        match="Loan amount must be greater than zero.",
    ):
        assess_loan(
            monthly_income=80000,
            existing_monthly_emi=0,
            loan_amount=0,
            loan_tenure_months=60,
            loan_purpose="PERSONAL",
            credit_score=750,
        )


def test_invalid_tenure():
    with pytest.raises(
        ValueError,
        match="Loan tenure must be greater than zero.",
    ):
        assess_loan(
            monthly_income=80000,
            existing_monthly_emi=0,
            loan_amount=500000,
            loan_tenure_months=0,
            loan_purpose="PERSONAL",
            credit_score=750,
        )


def test_negative_credit_score():
    with pytest.raises(
        ValueError,
        match="Credit score cannot be negative.",
    ):
        assess_loan(
            monthly_income=80000,
            existing_monthly_emi=0,
            loan_amount=500000,
            loan_tenure_months=60,
            loan_purpose="PERSONAL",
            credit_score=-1,
        )