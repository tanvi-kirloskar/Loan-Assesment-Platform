from pydantic import BaseModel


class LoanApplicationCreate(BaseModel):
    full_name: str
    monthly_income: int
    loan_amount: int
    loan_tenure_months: int


class LoanApplicationResponse(BaseModel):
    id: int
    full_name: str
    monthly_income: int
    loan_amount: int
    loan_tenure_months: int
    status: str

    class Config:
        from_attributes = True