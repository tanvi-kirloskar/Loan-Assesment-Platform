# Loan Assessment Policy

## Credit Score
The configured minimum credit score for deterministic D3 assessment is 600.
A credit score below this threshold causes the D3 assessment to be REJECTED.

## FOIR
The configured maximum FOIR is 50%.
FOIR above this threshold causes the D3 assessment to be REJECTED.

## Loan To Income
The configured maximum loan-to-income ratio is 5.00 times annual income.
LTI above this threshold causes the D3 assessment to be REJECTED.

## Verification Findings
Identity, employer, income, and cross-document discrepancies are verification findings.
A missing required document or unavailable evidence requires additional information.
A material identity or evidence discrepancy can be routed for HUMAN_REVIEW.

## AI Explanation
AI-generated explanations must describe the deterministic assessment and relevant policy evidence.
The AI explanation must not replace the deterministic D3 assessment or independently approve or reject an application.
