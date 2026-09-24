import AssessmentMetrics from "./AssessmentMetrics";
import DocumentsSection from "./DocumentsSection";
import { LOAN_PURPOSE_OPTIONS } from "./LoanApplicationForm";
import { currencyFormatter, getAssessmentReasons, hasValue } from "../utils/assessment";

function purposeLabel(value) {
  const match = LOAN_PURPOSE_OPTIONS.find((option) => option.value === value);
  return match ? match.label : value;
}

function titleCase(value) {
  if (typeof value !== "string" || value.length === 0) return value;
  return value.charAt(0) + value.slice(1).toLowerCase();
}

export default function ApplicationDetail({
  application,
  onBack,
  onSessionExpired,
}) {
  const decision = (application.decision || "").toUpperCase();
  const isApproved = decision === "APPROVED";
  const isRejected = decision === "REJECTED";

  const decisionClass = isApproved
    ? "result-approved"
    : isRejected
    ? "result-rejected"
    : "result-pending";

  const reasonItems = getAssessmentReasons(application.assessment_reasons);

  return (
    <div className="application-detail">
      <button type="button" className="detail-back-link" onClick={onBack}>
        ← Back to Dashboard
      </button>

      <div className={`detail-record-header ${decisionClass}`}>
        <div>
          <p className="detail-record-id">Application #{application.id}</p>
          <p className="detail-record-purpose">
            {purposeLabel(application.loan_purpose)} Loan
          </p>
          <p className="detail-record-amount">
            {currencyFormatter.format(application.loan_amount)}
          </p>
        </div>
        <span className="decision-badge" role="status">
          {decision || "PENDING"}
        </span>
      </div>

      <div className="detail-columns">
        <div className="detail-section detail-column">
          <h3 className="detail-section-heading">Application Details</h3>

          {hasValue(application.full_name) && (
            <div className="result-row">
              <span className="result-label">Applicant</span>
              <span className="result-value">{application.full_name}</span>
            </div>
          )}

          <div className="result-row">
            <span className="result-label">Loan Purpose</span>
            <span className="result-value">
              {purposeLabel(application.loan_purpose)}
            </span>
          </div>

          <div className="result-row">
            <span className="result-label">Loan Amount</span>
            <span className="result-value">
              {currencyFormatter.format(application.loan_amount)}
            </span>
          </div>

          <div className="result-row">
            <span className="result-label">Loan Tenure</span>
            <span className="result-value">
              {application.loan_tenure_months} months
            </span>
          </div>

          {hasValue(application.monthly_income) && (
            <div className="result-row">
              <span className="result-label">Monthly Income</span>
              <span className="result-value">
                {currencyFormatter.format(application.monthly_income)}
              </span>
            </div>
          )}

          <div className="result-row">
            <span className="result-label">Existing Monthly EMI</span>
            <span className="result-value">
              {currencyFormatter.format(application.existing_monthly_emi)}
            </span>
          </div>

          {hasValue(application.credit_score) && (
            <div className="result-row">
              <span className="result-label">Credit Score</span>
              <span className="result-value">
                {application.credit_score}
                {application.credit_score_source
                  ? ` (${titleCase(application.credit_score_source)})`
                  : ""}
              </span>
            </div>
          )}
        </div>

        <div className="detail-section detail-column">
          <h3 className="detail-section-heading">Assessment</h3>
          <AssessmentMetrics application={application} />

          {isRejected && reasonItems.length > 0 && (
            <div className="assessment-reasons">
              <p className="assessment-reasons-heading">Assessment Factors</p>
              <ul className="assessment-reasons-list">
                {reasonItems.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      <div className="detail-section detail-section-full">
        <DocumentsSection
          applicationId={application.id}
          onSessionExpired={onSessionExpired}
        />
      </div>
    </div>
  );
}
