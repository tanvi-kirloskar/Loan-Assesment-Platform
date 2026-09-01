def assess_loan(monthly_income: int, loan_amount: int) -> dict:
    loan_to_income_ratio = loan_amount / monthly_income

    if loan_to_income_ratio <= 10:
        decision = "approved"
        reason = "Loan amount is within the acceptable income ratio."
    else:
        decision = "rejected"
        reason = "Loan amount is too high relative to monthly income."

    return {
        "decision": decision,
        "loan_to_income_ratio": round(loan_to_income_ratio, 2),
        "reason": reason,
    }