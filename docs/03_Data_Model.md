# Data Model

## ERD
```mermaid
erDiagram
    USER ||--o| APPLICANT : owns
    APPLICANT ||--o{ LOAN_APPLICATION : submits
    LOAN_APPLICATION ||--o{ DOCUMENT : contains
    DOCUMENT ||--o{ DOCUMENT_EVIDENCE : produces
    LOAN_APPLICATION ||--o{ VERIFICATION_RUN : has
    VERIFICATION_RUN ||--o{ VERIFICATION_FINDING : produces
    LOAN_APPLICATION ||--o{ AUDIT_LOG : records
    USER ||--o{ AUDIT_LOG : acts

    USER { int id PK string email string password_hash string role }
    APPLICANT { int id PK int user_id FK string full_name int age string employment_type string employer int years_employed int monthly_income }
    LOAN_APPLICATION { int id PK int applicant_id FK decimal loan_amount int loan_tenure_months string loan_purpose decimal existing_monthly_emi string status string decision int credit_score string credit_score_source decimal interest_rate decimal emi decimal foir decimal lti string assessment_reasons }
    DOCUMENT { uuid id PK int application_id FK string document_type string original_filename string storage_key string mime_type int file_size string file_hash boolean is_active int version_number string status }
    DOCUMENT_EVIDENCE { int id PK uuid document_id FK string field_name string extracted_value decimal confidence }
    VERIFICATION_RUN { int id PK int application_id FK int run_number string status boolean is_latest }
    VERIFICATION_FINDING { int id PK int application_id FK int run_id FK string finding_type string severity string message string action }
    AUDIT_LOG { int id PK int application_id FK int actor_id FK string actor_role string action string previous_status string new_status string notes }
```

## Persistence Principles
- Assessment reasons are separate from the final advisor decision.
- Documents are versioned using hashes, version numbers, active status and storage keys.
- Each verification execution creates a run; historical runs remain preserved.
- Findings belong to a specific verification run.
- Audit logs record actor, role, action, status transition and notes.

## Database Management
Alembic manages schema migrations. The backend currently uses PostgreSQL locally and Amazon RDS in the AWS deployment.
