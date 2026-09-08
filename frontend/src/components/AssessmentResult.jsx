import AssessmentMetrics from "./AssessmentMetrics";
import { LOAN_PURPOSE_OPTIONS } from "./LoanApplicationForm";
import { currencyFormatter, getAssessmentReasons, hasValue } from "../utils/assessment";

function purposeLabel(value) {
  const match = LOAN_PURPOSE_OPTIONS.find((option) => option.value === value);
  return match ? match.label : value;
}

export default function AssessmentResult({ application, onReset, onBackToDashboard }) {
  const decision = (application.decision || "").toUpperCase();
  const isApproved = decision === "APPROVED";
  const isRejected = decision === "REJECTED";

  const decisionClass = isApproved
    ? "assessment-approved"
    : isRejected
    ? "assessment-rejected"
    : "assessment-pending";

  const summaryText = isApproved
    ? "Your application meets the configured assessment criteria."
    : isRejected
    ? "Your application does not meet one or more configured criteria."
    : "Your application status is pending assessment.";

  const reasonItems = getAssessmentReasons(application.assessment_reasons);

  return (
    <div className={`assessment-result ${decisionClass}`}>
      <p className="assessment-eyebrow">Assessment Outcome</p>

      <div className="assessment-decision-block">
        <span className="assessment-decision-badge" role="status">
          {decision || "PENDING"}
        </span>
        <p className="assessment-summary">{summaryText}</p>
      </div>

      <div className="assessment-financial-section">
        <h3 className="detail-section-heading">Financial Assessment</h3>
        <AssessmentMetrics application={application} />
      </div>

      <div className="assessment-summary-section">
        <h3 className="detail-section-heading">Application Summary</h3>
        <div className="result-row">
          <span className="result-label">Loan Amount</span>
          <span className="result-value">
            {currencyFormatter.format(application.loan_amount)}
          </span>
        </div>
        <div className="result-row">
          <span className="result-label">Tenure</span>
          <span className="result-value">
            {application.loan_tenure_months} months
          </span>
        </div>
        {hasValue(application.credit_score) && (
          <div className="result-row">
            <span className="result-label">Credit Score</span>
            <span className="result-value">{application.credit_score}</span>
          </div>
        )}
        <div className="result-row">
          <span className="result-label">Purpose</span>
          <span className="result-value">
            {purposeLabel(application.loan_purpose)} Loan
          </span>
        </div>
      </div>

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

      <div className="assessment-actions">
        <button type="button" className="submit-button" onClick={onReset}>
          Submit Another Application
        </button>
        {onBackToDashboard && (
          <button
            type="button"
            className="secondary-button"
            onClick={onBackToDashboard}
          >
            Back to Dashboard
          </button>
        )}
      </div>
    </div>
  );
}
