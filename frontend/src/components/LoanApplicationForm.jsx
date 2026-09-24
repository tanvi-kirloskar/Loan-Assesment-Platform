import { useState } from "react";

export const LOAN_PURPOSE_OPTIONS = [
  { label: "Personal", value: "PERSONAL" },
  { label: "Home", value: "HOME" },
  { label: "Education", value: "EDUCATION" },
  { label: "Medical", value: "MEDICAL" },
  { label: "Business", value: "BUSINESS" },
  { label: "Other", value: "OTHER" },
];

const DOCUMENT_REQUIREMENTS = [
  { label: "Payslip", value: "PAYSLIP" },
  { label: "Bank Statement", value: "BANK_STATEMENT" },
  { label: "Tax Return", value: "TAX_RETURN" },
];

const ALLOWED_MIME_TYPES = ["application/pdf", "image/png", "image/jpeg"];
const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;

const initialValues = {
  full_name: "",
  monthly_income: "",
  loan_amount: "",
  loan_tenure_months: "",
  loan_purpose: "",
  existing_monthly_emi: "",
  credit_score: "",
};

function validate(values, documents) {
  const errors = {};

  if (!values.full_name.trim()) {
    errors.full_name = "Full name is required.";
  }

  if (values.monthly_income === "" || Number(values.monthly_income) <= 0) {
    errors.monthly_income = "Monthly income must be greater than 0.";
  }

  if (values.loan_amount === "" || Number(values.loan_amount) <= 0) {
    errors.loan_amount = "Loan amount must be greater than 0.";
  }

  if (
    values.loan_tenure_months === "" ||
    Number(values.loan_tenure_months) <= 0
  ) {
    errors.loan_tenure_months = "Loan tenure must be greater than 0.";
  }

  if (!values.loan_purpose) {
    errors.loan_purpose = "Please select a loan purpose.";
  }

  if (
    values.existing_monthly_emi === "" ||
    Number(values.existing_monthly_emi) < 0
  ) {
    errors.existing_monthly_emi =
      "Existing monthly EMI is required (enter 0 if none).";
  }

  if (values.credit_score === "") {
    errors.credit_score = "Credit score is required.";
  } else if (
    !Number.isInteger(Number(values.credit_score)) ||
    Number(values.credit_score) < 300 ||
    Number(values.credit_score) > 900
  ) {
    errors.credit_score = "Enter a valid credit score between 300 and 900.";
  }

  DOCUMENT_REQUIREMENTS.forEach(({ label, value }) => {
    const file = documents[value];

    if (!file) {
      errors[value] = `${label} is required.`;
      return;
    }

    if (!ALLOWED_MIME_TYPES.includes(file.type)) {
      errors[value] = "Only PDF, PNG or JPEG files are supported.";
    } else if (file.size > MAX_FILE_SIZE_BYTES) {
      errors[value] = "File must be 5 MB or smaller.";
    }
  });

  return errors;
}

function blurOnWheel(event) {
  event.target.blur();
}

function formatFileSize(bytes) {
  if (!Number.isFinite(bytes)) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function LoanApplicationForm({ onSubmit, isSubmitting }) {
  const [values, setValues] = useState(initialValues);
  const [documents, setDocuments] = useState({
    PAYSLIP: null,
    BANK_STATEMENT: null,
    TAX_RETURN: null,
  });
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  function handleChange(field, value) {
    setValues((prev) => ({ ...prev, [field]: value }));
  }

  function handleBlur(field) {
    setTouched((prev) => ({ ...prev, [field]: true }));
    setErrors(validate(values, documents));
  }

  function handleDocumentChange(documentType, file) {
    setDocuments((prev) => ({
      ...prev,
      [documentType]: file || null,
    }));
    setTouched((prev) => ({
      ...prev,
      [documentType]: true,
    }));
    setErrors(
      validate(values, {
        ...documents,
        [documentType]: file || null,
      })
    );
  }

  function handleSubmit(event) {
    event.preventDefault();

    const validationErrors = validate(values, documents);
    setErrors(validationErrors);
    setTouched({
      full_name: true,
      monthly_income: true,
      loan_amount: true,
      loan_tenure_months: true,
      loan_purpose: true,
      existing_monthly_emi: true,
      credit_score: true,
      PAYSLIP: true,
      BANK_STATEMENT: true,
      TAX_RETURN: true,
    });

    if (Object.keys(validationErrors).length > 0) {
      return;
    }

    onSubmit({
      full_name: values.full_name.trim(),
      monthly_income: Number(values.monthly_income),
      loan_amount: Number(values.loan_amount),
      loan_tenure_months: Number(values.loan_tenure_months),
      loan_purpose: values.loan_purpose,
      existing_monthly_emi: Number(values.existing_monthly_emi),
      credit_score: Number(values.credit_score),
      credit_score_source: "MOCK",
      documents,
    });
  }

  const documentsComplete = DOCUMENT_REQUIREMENTS.every(
    ({ value }) => documents[value]
  );

  return (
    <>
      <div className="form-journey" aria-hidden="true">
        <span className="form-journey-step form-journey-step-active">
          01 Applicant
        </span>
        <span className="form-journey-step form-journey-step-active">
          02 Loan Details
        </span>
        <span className="form-journey-step form-journey-step-active">
          03 Financial Profile
        </span>
        <span className="form-journey-step form-journey-step-active">
          04 Required Documents
        </span>
        <span className="form-journey-step">05 Assessment</span>
      </div>

      <form className="application-form" onSubmit={handleSubmit} noValidate>
        <fieldset className="form-section">
          <legend className="form-section-legend">Applicant</legend>

          <div className="form-row">
            <div className="form-field">
              <label htmlFor="full_name">Full name</label>
              <input
                id="full_name"
                type="text"
                value={values.full_name}
                onChange={(e) => handleChange("full_name", e.target.value)}
                onBlur={() => handleBlur("full_name")}
                aria-invalid={touched.full_name && !!errors.full_name}
                aria-describedby={
                  errors.full_name ? "full_name-error" : undefined
                }
                placeholder="e.g. Tanvi Sharma"
                autoComplete="name"
              />
              {touched.full_name && errors.full_name && (
                <p className="field-error" id="full_name-error">
                  {errors.full_name}
                </p>
              )}
            </div>

            <div className="form-field">
              <label htmlFor="monthly_income">Monthly income (₹)</label>
              <input
                id="monthly_income"
                type="number"
                min="0"
                step="1"
                inputMode="numeric"
                onWheel={blurOnWheel}
                value={values.monthly_income}
                onChange={(e) =>
                  handleChange("monthly_income", e.target.value)
                }
                onBlur={() => handleBlur("monthly_income")}
                aria-invalid={
                  touched.monthly_income && !!errors.monthly_income
                }
                aria-describedby={
                  errors.monthly_income ? "monthly_income-error" : undefined
                }
                placeholder="80000"
              />
              {touched.monthly_income && errors.monthly_income && (
                <p className="field-error" id="monthly_income-error">
                  {errors.monthly_income}
                </p>
              )}
            </div>
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend className="form-section-legend">Loan Request</legend>

          <div className="form-row">
            <div className="form-field">
              <label htmlFor="loan_amount">Loan amount (₹)</label>
              <input
                id="loan_amount"
                type="number"
                min="0"
                step="1"
                inputMode="numeric"
                onWheel={blurOnWheel}
                value={values.loan_amount}
                onChange={(e) => handleChange("loan_amount", e.target.value)}
                onBlur={() => handleBlur("loan_amount")}
                aria-invalid={touched.loan_amount && !!errors.loan_amount}
                aria-describedby={
                  errors.loan_amount ? "loan_amount-error" : undefined
                }
                placeholder="500000"
              />
              {touched.loan_amount && errors.loan_amount && (
                <p className="field-error" id="loan_amount-error">
                  {errors.loan_amount}
                </p>
              )}
            </div>

            <div className="form-field">
              <label htmlFor="loan_tenure_months">Loan tenure (months)</label>
              <input
                id="loan_tenure_months"
                type="number"
                min="0"
                step="1"
                inputMode="numeric"
                onWheel={blurOnWheel}
                value={values.loan_tenure_months}
                onChange={(e) =>
                  handleChange("loan_tenure_months", e.target.value)
                }
                onBlur={() => handleBlur("loan_tenure_months")}
                aria-invalid={
                  touched.loan_tenure_months && !!errors.loan_tenure_months
                }
                aria-describedby={
                  errors.loan_tenure_months
                    ? "loan_tenure_months-error"
                    : undefined
                }
                placeholder="60"
              />
              {touched.loan_tenure_months && errors.loan_tenure_months && (
                <p className="field-error" id="loan_tenure_months-error">
                  {errors.loan_tenure_months}
                </p>
              )}
            </div>
          </div>

          <div className="form-field">
            <label htmlFor="loan_purpose">Loan purpose</label>
            <select
              id="loan_purpose"
              value={values.loan_purpose}
              onChange={(e) => handleChange("loan_purpose", e.target.value)}
              onBlur={() => handleBlur("loan_purpose")}
              aria-invalid={touched.loan_purpose && !!errors.loan_purpose}
              aria-describedby={
                errors.loan_purpose ? "loan_purpose-error" : undefined
              }
            >
              <option value="" disabled>
                Select a purpose
              </option>
              {LOAN_PURPOSE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {touched.loan_purpose && errors.loan_purpose && (
              <p className="field-error" id="loan_purpose-error">
                {errors.loan_purpose}
              </p>
            )}
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend className="form-section-legend">Financial Profile</legend>

          <div className="form-row">
            <div className="form-field">
              <label htmlFor="existing_monthly_emi">
                Existing monthly EMI (₹)
              </label>
              <input
                id="existing_monthly_emi"
                type="number"
                min="0"
                step="1"
                inputMode="numeric"
                onWheel={blurOnWheel}
                value={values.existing_monthly_emi}
                onChange={(e) =>
                  handleChange("existing_monthly_emi", e.target.value)
                }
                onBlur={() => handleBlur("existing_monthly_emi")}
                aria-invalid={
                  touched.existing_monthly_emi &&
                  !!errors.existing_monthly_emi
                }
                aria-describedby={
                  errors.existing_monthly_emi
                    ? "existing_monthly_emi-error"
                    : undefined
                }
                placeholder="0"
              />
              {touched.existing_monthly_emi &&
                errors.existing_monthly_emi && (
                  <p className="field-error" id="existing_monthly_emi-error">
                    {errors.existing_monthly_emi}
                  </p>
                )}
            </div>

            <div className="form-field">
              <label htmlFor="credit_score">Credit score</label>
              <input
                id="credit_score"
                type="number"
                min="300"
                max="900"
                step="1"
                inputMode="numeric"
                onWheel={blurOnWheel}
                value={values.credit_score}
                onChange={(e) => handleChange("credit_score", e.target.value)}
                onBlur={() => handleBlur("credit_score")}
                aria-invalid={touched.credit_score && !!errors.credit_score}
                aria-describedby={
                  errors.credit_score
                    ? "credit_score-error"
                    : "credit_score-help"
                }
                placeholder="742"
              />
              {touched.credit_score && errors.credit_score ? (
                <p className="field-error" id="credit_score-error">
                  {errors.credit_score}
                </p>
              ) : (
                <p className="field-help" id="credit_score-help">
                  Used as an input to the policy-based assessment.
                </p>
              )}
            </div>
          </div>
        </fieldset>

        <fieldset className="form-section required-documents-section">
          <legend className="form-section-legend">Required Documents</legend>
          <p className="field-help required-documents-help">
            All three documents are required to submit your application. PDF,
            PNG or JPEG · Maximum 5 MB each.
          </p>

          <div className="required-document-list">
            {DOCUMENT_REQUIREMENTS.map(({ label, value }) => {
              const file = documents[value];
              const error = errors[value];
              const inputId = `required-${value.toLowerCase()}`;

              return (
                <div className="required-document-card" key={value}>
                  <div className="required-document-info">
                    <div>
                      <p className="required-document-label">
                        {label}
                        <span className="required-document-mark">
                          Required
                        </span>
                      </p>
                      <p className="required-document-filename">
                        {file
                          ? `${file.name} · ${formatFileSize(file.size)}`
                          : "No document selected"}
                      </p>
                    </div>

                    <label
                      className="upload-choose-button"
                      htmlFor={inputId}
                    >
                      {file ? "Change Document" : "Choose Document"}
                    </label>
                    <input
                      id={inputId}
                      type="file"
                      accept=".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg"
                      onChange={(event) =>
                        handleDocumentChange(
                          value,
                          event.target.files?.[0] || null
                        )
                      }
                      hidden
                    />
                  </div>

                  {touched[value] && error && (
                    <p className="field-error" role="alert">
                      {error}
                    </p>
                  )}
                </div>
              );
            })}
          </div>

          {!documentsComplete && (
            <p className="required-documents-status">
              Select all three required documents to enable submission.
            </p>
          )}
        </fieldset>

        <div className="form-actions">
          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting || !documentsComplete}
          >
            {isSubmitting ? "Submitting…" : "Submit Application"}
          </button>
        </div>
      </form>
    </>
  );
}
