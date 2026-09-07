# D3 — Deterministic Financial Assessment Engine

## Purpose

The D3 engine calculates deterministic financial metrics and produces a structured loan assessment.

## Inputs

- Monthly income
- Existing monthly EMI
- Loan amount
- Loan tenure in months
- Loan purpose
- Credit score

## Outputs

- Decision
- Indicative annual interest rate
- Proposed EMI
- FOIR
- LTI
- Assessment reasons

## Interest Rate

Base Rate:

8.00%

Credit Score Premium:

- >= 750: 0.00%
- 700–749: 0.50%
- 650–699: 1.00%
- 600–649: 2.00%
- < 600: 3.00%

Loan Purpose Adjustment:

- PERSONAL: +0.50%
- HOME: +0.00%
- EDUCATION: +0.25%
- MEDICAL: +0.25%
- BUSINESS: +0.75%
- OTHER: +1.00%

## Assessment Rules

- Minimum credit score: 600
- Maximum FOIR: 50%
- Maximum LTI: 5x

## FOIR

FOIR =
(existing monthly EMI + proposed EMI) / monthly income × 100

Fixed obligations are not included in D3.

## LTI

LTI =
loan amount / (monthly income × 12)

## Example

Monthly income: ₹80,000
Existing EMI: ₹10,000
Loan amount: ₹5,00,000
Tenure: 60 months
Credit score: 742
Purpose: PERSONAL

Expected annual interest rate: 9.00%
Expected EMI: approximately ₹10,379.18
Expected FOIR: approximately 25.47%
Expected LTI: approximately 0.52x
Expected decision: APPROVED
