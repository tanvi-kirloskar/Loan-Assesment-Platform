# Development Log

## Day 1 — Backend Foundation

### Completed

- Initialized FastAPI backend
- Configured PostgreSQL connection
- Created SQLAlchemy `LoanApplication` model
- Created Pydantic request/response schemas
- Implemented `POST /applications`
- Verified persistence in PostgreSQL

### Validation

- Successfully submitted test application through Swagger
- Verified records using PostgreSQL queries

### Outcome

Loan applications can now be submitted through the API
and persisted in PostgreSQL.

---

## Day 2 — Application Retrieval

### Completed

- Added `GET /applications/{application_id}`
- Added 404 handling for missing applications
- Verified endpoint through Swagger
- Verified registered routes programmatically

### Outcome

Applications can now be created and retrieved through the API.