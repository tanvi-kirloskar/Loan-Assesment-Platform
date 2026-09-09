from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class LoanApplicationCreate(BaseModel):
    full_name: str
    monthly_income: int
    loan_amount: int
    loan_tenure_months: int
    loan_purpose: str
    existing_monthly_emi: int
    credit_score: int
    credit_score_source: str = "MOCK"


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

    interest_rate: float | None
    emi: float | None
    foir: float | None
    lti: float | None
    assessment_reasons: str | None

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: UUID
    application_id: int
    document_type: str
    original_filename: str
    mime_type: str
    file_size: int
    status: str
    created_at: datetime

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
