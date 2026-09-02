from pydantic import BaseModel


class LoanApplicationCreate(BaseModel):
    full_name: str
    monthly_income: int
    loan_amount: int
    loan_tenure_months: int
    loan_purpose: str
    existing_monthly_emi: int


class LoanApplicationResponse(BaseModel):
    id: int
    applicant_id: int
    loan_amount: int
    loan_tenure_months: int
    loan_purpose: str | None
    existing_monthly_emi: int | None
    status: str
    decision: str | None
    credit_score: int | None
    credit_score_source: str | None

    class Config:
        from_attributes = True

class RegisterRequest(BaseModel):
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str