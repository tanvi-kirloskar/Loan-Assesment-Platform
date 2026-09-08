import AssessmentMetrics from "./AssessmentMetrics";
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

export default function ApplicationDetail({ application, onBack }) {
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

      <p className="result-heading">Application #{application.id}</p>

      <div className="detail-section">
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

      <div className={`detail-section ${decisionClass}`}>
        <div className="detail-assessment-heading-row">
          <h3 className="detail-section-heading">Assessment</h3>
          <span className="decision-badge" role="status">
            {decision || "PENDING"}
          </span>
        </div>

        <AssessmentMetrics application={application} />

        {isRejected && reasonItems.length > 0 && (
          <div className="assessment-reasons">
            <p className="assessment-reasons-heading">Assessment Reasons</p>
            <ul className="assessment-reasons-list">
              {reasonItems.map((reason, index) => (
                <li key={index}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
