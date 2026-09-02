const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const statusLabels = {
  submitted: "Submitted",
  flagged: "Flagged for review",
  approved: "Approved",
  rejected: "Rejected",
};

export default function ResultCard({ application, onReset }) {
  const decision = (application.decision || "").toLowerCase();
  const isApproved = decision === "approved";
  const isRejected = decision === "rejected";

  const decisionClass = isApproved
    ? "result-approved"
    : isRejected
    ? "result-rejected"
    : "result-pending";

  const statusLabel =
    statusLabels[application.status] || application.status;

  return (
    <div className={`result-card ${decisionClass}`}>
      <p className="result-heading">Application Submitted</p>

      <div className="result-row">
        <span className="result-label">Application ID</span>
        <span className="result-value">#{application.id}</span>
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

      <div className="result-row">
        <span className="result-label">Loan Purpose</span>
        <span className="result-value">{application.loan_purpose}</span>
      </div>

      <div className="result-row">
        <span className="result-label">Existing Monthly EMI</span>
        <span className="result-value">
          {currencyFormatter.format(application.existing_monthly_emi)}
        </span>
      </div>

      <div className="result-row">
        <span className="result-label">Application Status</span>
        <span className="result-value">{statusLabel}</span>
      </div>

      {application.credit_score !== null &&
        application.credit_score !== undefined && (
          <div className="result-row">
            <span className="result-label">Credit Score</span>
            <span className="result-value">
              {application.credit_score}
              {application.credit_score_source
                ? ` (${application.credit_score_source})`
                : ""}
            </span>
          </div>
        )}

      <div className="decision-badge-row">
        <span className="result-label">Decision</span>
        <span className="decision-badge" role="status">
          {decision ? decision.toUpperCase() : "PENDING"}
        </span>
      </div>

      <button type="button" className="secondary-button" onClick={onReset}>
        Submit Another Application
      </button>
    </div>
  );
}
