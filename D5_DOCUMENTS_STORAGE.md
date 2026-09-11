# D5 Documents & Storage Design

## Objective

D5 adds secure supporting-document management to the AI Loan Assessment & Advisory Platform.

Authenticated applicants can attach supporting documents to their own loan applications. The backend validates files, stores document metadata in PostgreSQL, stores file bytes through a replaceable storage provider, and enforces application ownership.

D5 focuses on document ingestion and storage. Document understanding, AI extraction, RAG, risk reasoning, and human review belong to later milestones.

---

## Architecture

```text
React
  |
  | multipart/form-data
  v
FastAPI
  |
  +----------------------+-------------------+
  |                      |                   |
  v                      v                   |
Authentication       Authorization           |
                         |                   |
                         +--------+----------+
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
              StorageProvider             PostgreSQL
                    |                           |
             +------+-----+                     |
             |            |                     |
             v            v                     v
         Local Disk      S3              Document metadata