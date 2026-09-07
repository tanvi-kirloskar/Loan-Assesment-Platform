from decimal import Decimal, ROUND_HALF_UP


BASE_RATE = Decimal("0.08")

MIN_CREDIT_SCORE = 600
MAX_FOIR = Decimal("50.00")
MAX_LTI = Decimal("5.00")


CREDIT_SCORE_PREMIUMS = {
    "750+": Decimal("0.00"),
    "700-749": Decimal("0.005"),
    "650-699": Decimal("0.01"),
    "600-649": Decimal("0.02"),
    "below-600": Decimal("0.03"),
}


PURPOSE_ADJUSTMENTS = {
    "PERSONAL": Decimal("0.005"),
    "HOME": Decimal("0.00"),
    "EDUCATION": Decimal("0.0025"),
    "MEDICAL": Decimal("0.0025"),
    "BUSINESS": Decimal("0.0075"),
    "OTHER": Decimal("0.01"),
}


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _round_percentage(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _get_credit_score_premium(credit_score: int) -> Decimal:
    if credit_score >= 750:
        return CREDIT_SCORE_PREMIUMS["750+"]
    if credit_score >= 700:
        return CREDIT_SCORE_PREMIUMS["700-749"]
    if credit_score >= 650:
        return CREDIT_SCORE_PREMIUMS["650-699"]
    if credit_score >= 600:
        return CREDIT_SCORE_PREMIUMS["600-649"]
    return CREDIT_SCORE_PREMIUMS["below-600"]


def _get_purpose_adjustment(loan_purpose: str) -> Decimal:
    return PURPOSE_ADJUSTMENTS.get(loan_purpose.upper(), PURPOSE_ADJUSTMENTS["OTHER"])


def _calculate_interest_rate(
    credit_score: int,
    loan_purpose: str,
) -> Decimal:
    return (
        BASE_RATE
        + _get_credit_score_premium(credit_score)
        + _get_purpose_adjustment(loan_purpose)
    )


def _calculate_emi(
    loan_amount: Decimal,
    annual_interest_rate: Decimal,
    tenure_months: int,
) -> Decimal:
    monthly_rate = annual_interest_rate / Decimal("12")

    growth_factor = (Decimal("1") + monthly_rate) ** tenure_months

    emi = (
        loan_amount
        * monthly_rate
        * growth_factor
        / (growth_factor - Decimal("1"))
    )

    return _round_money(emi)


def _calculate_foir(
    existing_monthly_emi: Decimal,
    proposed_emi: Decimal,
    monthly_income: Decimal,
) -> Decimal:
    foir = (
        (existing_monthly_emi + proposed_emi)
        / monthly_income
        * Decimal("100")
    )

    return _round_percentage(foir)


def _calculate_lti(
    loan_amount: Decimal,
    monthly_income: Decimal,
) -> Decimal:
    annual_income = monthly_income * Decimal("12")
    lti = loan_amount / annual_income

    return lti.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def assess_loan(
    monthly_income: int,
    existing_monthly_emi: int,
    loan_amount: int,
    loan_tenure_months: int,
    loan_purpose: str,
    credit_score: int,
) -> dict:
    if monthly_income <= 0:
        raise ValueError("Monthly income must be greater than zero.")

    if existing_monthly_emi < 0:
        raise ValueError("Existing monthly EMI cannot be negative.")

    if loan_amount <= 0:
        raise ValueError("Loan amount must be greater than zero.")

    if loan_tenure_months <= 0:
        raise ValueError("Loan tenure must be greater than zero.")

    if credit_score < 0:
        raise ValueError("Credit score cannot be negative.")

    income = Decimal(monthly_income)
    existing_emi = Decimal(existing_monthly_emi)
    principal = Decimal(loan_amount)

    interest_rate = _calculate_interest_rate(
        credit_score=credit_score,
        loan_purpose=loan_purpose,
    )

    emi = _calculate_emi(
        loan_amount=principal,
        annual_interest_rate=interest_rate,
        tenure_months=loan_tenure_months,
    )

    foir = _calculate_foir(
        existing_monthly_emi=existing_emi,
        proposed_emi=emi,
        monthly_income=income,
    )

    lti = _calculate_lti(
        loan_amount=principal,
        monthly_income=income,
    )

    reasons = []

    if credit_score < MIN_CREDIT_SCORE:
        reasons.append("Credit score is below configured minimum.")

    if foir > MAX_FOIR:
        reasons.append("FOIR exceeds configured threshold.")

    if lti > MAX_LTI:
        reasons.append("LTI exceeds configured threshold.")

    decision = "APPROVED" if not reasons else "REJECTED"

    return {
        "decision": decision,
        "interest_rate": interest_rate,
        "emi": emi,
        "foir": foir,
        "lti": lti,
        "reasons": reasons,
    }