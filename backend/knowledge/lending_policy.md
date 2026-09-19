# Loan Assessment Policy

## 1. Purpose

This policy defines the rules used by the loan assessment platform
to evaluate financial eligibility, verify applicant information,
and determine when an application requires additional human review.

The policy is intended to support consistent and explainable
loan assessment workflows.

---

## 2. Income Verification

The applicant's declared monthly income should be supported by
the submitted income documents.

For a payslip:

- Declared monthly income should be compared with the gross salary
  stated on the payslip.
- An exact match is treated as an income verification match.
- A mismatch should generate a verification finding requiring review.

The verification system should not silently modify the applicant's
declared income based on document evidence.

---

## 3. Bank Statement Salary Verification

Where a bank statement is available, the salary credit may be
compared with the income reported in the payslip.

- A matching salary amount produces an informational verification
  finding.
- A mismatch produces a warning finding requiring review.
- Missing salary evidence should produce a finding indicating that
  cross-document verification could not be completed.

Bank statement evidence should support verification rather than
automatically changing the applicant's declared income.

---

## 4. Tax Return Income Verification

Where a tax return is available, the reported annual gross income
may be compared with the applicant's declared monthly income.

The declared monthly income can be annualized as:

    Monthly Income × 12

The annualized amount can then be compared with the gross total
income reported in the tax return.

- A matching amount produces an informational finding.
- A mismatch produces a warning finding requiring review.
- Missing gross-income evidence produces a warning finding.

---

## 5. Payslip and Tax Return Consistency

Where both documents are available, annualized payslip gross income
may be compared with tax-return gross total income.

The payslip monthly gross income is annualized as:

    Monthly Gross Income × 12

- A matching amount produces an informational finding.
- A mismatch produces a warning finding requiring review.
- Missing evidence from either document prevents the comparison
  from being completed.

---

## 6. Applicant Identity Verification

Applicant information should be checked against document evidence.

For applicant name:

- A matching name produces an informational finding.
- A mismatch produces a warning finding requiring review.

The verification process should report the discrepancy rather than
silently modifying applicant information.

---

## 7. Employer Verification

Where employer information is available in the application,
it may be compared with the employer stated on the payslip.

- A matching employer produces an informational finding.
- A mismatch produces a warning finding requiring review.
- If application employer information is unavailable, employer
  consistency cannot be fully verified.

---

## 8. Financial Assessment

The deterministic financial assessment engine remains responsible
for calculating financial assessment metrics and the resulting
assessment decision.

The assessment engine considers configured rules including:

- Interest rate
- EMI
- FOIR
- Loan-to-income ratio
- Credit score

Document verification findings provide supporting evidence and
verification context.

Document verification and AI-generated explanations should not
silently replace the deterministic financial assessment engine.

---

## 9. Human Review

An application should be considered for human review when verification
produces findings requiring review.

Examples include:

- Income mismatch
- Name mismatch
- Employer mismatch
- Salary mismatch between documents
- Tax-return income mismatch
- Missing required evidence
- Verification errors

Human review is intended to allow an authorized reviewer to examine
the underlying application, documents, evidence, and findings.

---

## 10. AI and Policy Explanation

AI-generated explanations should be grounded in the relevant policy
and application findings.

The AI explanation should:

- Refer to retrieved policy information.
- Explain the relevant finding.
- Distinguish documented evidence from interpretation.
- Avoid inventing policy requirements.
- Avoid silently changing deterministic assessment results.

The AI explanation is advisory and explanatory.

It does not replace the deterministic assessment engine or authorized
human review.

---

## 11. Evidence and Findings

The platform distinguishes between:

### Evidence

Information extracted from submitted documents.

Examples:

- Payslip gross income
- Bank salary credit
- Tax-return gross total income
- Employee name
- Employer

### Finding

An interpretation or comparison performed using application data
and/or document evidence.

Examples:

- INCOME_MATCH
- NAME_MISMATCH
- SALARY_CROSS_DOCUMENT_MATCH
- TAX_RETURN_INCOME_MATCH

### Action

The workflow response associated with a finding.

Examples:

- CONTINUE
- REVIEW

The distinction between evidence, finding, and action should be
preserved throughout the assessment workflow.