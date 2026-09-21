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
    is_active: bool
    version_number: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentEvidenceResponse(BaseModel):
    id: UUID
    document_id: UUID
    field_name: str
    extracted_value: str
    confidence: float | None
    created_at: datetime

    class Config:
        from_attributes = True

class DocumentRequirementResponse(BaseModel):
    document_type: str
    required: bool
    satisfied: bool
    active_document_id: UUID | None = None
    active_version: int | None = None
    active_filename: str | None = None


class VerificationRunResponse(BaseModel):
    id: UUID
    application_id: int
    run_number: int
    status: str
    is_latest: bool
    created_at: datetime
    completed_at: datetime | None = None

    class Config:
        from_attributes = True


class VerificationFindingResponse(BaseModel):
    id: UUID
    application_id: int
    finding_type: str
    severity: str
    message: str
    action: str
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


class AdvisorDocumentResponse(DocumentResponse):
    pass


class AdvisorEvidenceResponse(DocumentEvidenceResponse):
    pass


class AdvisorFindingResponse(VerificationFindingResponse):
    pass


class AdvisorApplicationSummaryResponse(BaseModel):
    id: int
    applicant_id: int
    applicant_name: str
    loan_amount: int
    status: str
    decision: str | None
    foir: float | None
    lti: float | None
    review_risk_score: int


class AdvisorApplicationDetailResponse(BaseModel):
    id: int
    applicant_id: int
    applicant_name: str
    loan_amount: int
    loan_tenure_months: int
    loan_purpose: str
    existing_monthly_emi: int
    status: str
    decision: str | None
    credit_score: int | None
    credit_score_source: str | None
    interest_rate: float | None
    emi: float | None
    foir: float | None
    lti: float | None
    review_risk_score: int
    review_risk_factors: list[dict]
    assessment_reasons: str | None
    documents: list[AdvisorDocumentResponse]
    evidence: list[AdvisorEvidenceResponse]
    findings: list[AdvisorFindingResponse]


class AdvisorVerificationRunResponse(BaseModel):
    id: UUID
    application_id: int
    run_number: int
    status: str
    is_latest: bool
    created_at: datetime
    completed_at: datetime | None


class AdvisorPolicyEvidenceResponse(BaseModel):
    source: str
    section: str
    content: str


class AdvisorReviewRiskFactorResponse(BaseModel):
    code: str
    label: str
    points: int


class AdvisorWorkflowResponse(BaseModel):
    route: str
    verification_run: AdvisorVerificationRunResponse | None
    policy_evidence: list[AdvisorPolicyEvidenceResponse]
    ai_explanation: str
    review_risk_score: int
    review_risk_factors: list[AdvisorReviewRiskFactorResponse]


class AdvisorDecisionRequest(BaseModel):
    action: str
    notes: str | None = None


class AdvisorAuditLogResponse(BaseModel):
    id: UUID
    application_id: int
    actor_id: int
    actor_role: str
    action: str
    previous_status: str | None
    new_status: str | None
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True
