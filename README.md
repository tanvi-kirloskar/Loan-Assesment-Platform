# AI Loan Assessment & Advisory Platform

A production-oriented, three-tier loan assessment platform that combines **deterministic financial assessment, document/evidence verification, policy-grounded AI assistance, and human advisor review**.

The platform is designed to demonstrate how an AI-assisted financial workflow can be built with clear separation between deterministic business logic, AI capabilities, and human decision-making.

---

## Overview

The platform processes a loan application through the following high-level workflow:

```text
Applicant
   │
   ▼
React Frontend
   │
   ▼
FastAPI Backend
   │
   ├── Authentication & Authorization
   │
   ├── Document Management
   │
   ├── Evidence Verification
   │
   ├── Deterministic Financial Assessment
   │
   ├── LangGraph Workflow
   │
   ├── Policy Retrieval (RAG)
   │
   ├── AI Explanation
   │
   └── Advisor Review
   │
   ▼
PostgreSQL