# Security & RBAC

## Authentication
- JWT access tokens.
- HTTP Bearer authentication.
- Password hashing through pwdlib.
- Token expiry.
- User lookup after token validation.

## Roles
- APPLICANT
- ADVISOR

Advisor APIs explicitly require the ADVISOR role. Applicant application queries are scoped to the authenticated applicant.

## AWS Secrets
Parameter Store supplies database configuration, S3 bucket configuration, Gemini API key and JWT secret. Sensitive parameters use SecureString where configured.

Secrets are not stored in source code.

## AWS IAM
EC2 uses an IAM instance role for:
- Systems Manager Session Manager;
- reading required application parameters.

GitHub Actions uses OIDC to assume the dedicated GitHub Actions IAM role rather than using a long-lived AWS access key.

## S3 Security
The document bucket has:
- public access blocked;
- AES256 server-side encryption;
- versioning enabled.

The application accesses documents through its storage provider rather than exposing the bucket publicly.

## Transport
Phase 1 currently uses HTTP. HTTPS/custom-domain configuration is deferred.

## Production Security Gaps
Phase 1 does not yet implement the complete production security stack such as WAF at the deployed edge, centralized secret rotation, advanced egress controls, multi-instance compute or production-grade observability.
