const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

export default function ResultCard({ application, onReset }) {
  const decision = (application.status || "").toLowerCase();
  const isApproved = decision === "approved";
  const isRejected = decision === "rejected";

  const statusClass = isApproved
    ? "result-approved"
    : isRejected
    ? "result-rejected"
    : "result-pending";

  return (
    <div className={`result-card ${statusClass}`}>
      <p className="result-heading">Application Submitted</p>

      <div className="result-row">
        <span className="result-label">Application ID</span>
        <span className="result-value">#{application.id}</span>
      </div>

      <div className="result-row">
        <span className="result-label">Applicant</span>
        <span className="result-value">{application.full_name}</span>
      </div>

      <div className="result-row">
        <span className="result-label">Monthly Income</span>
        <span className="result-value">
          {currencyFormatter.format(application.monthly_income)}
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

      <div className="decision-badge-row">
        <span className="result-label">Decision</span>
        <span className="decision-badge" role="status">
          {application.status.toUpperCase()}
        </span>
      </div>

      <button type="button" className="secondary-button" onClick={onReset}>
        Submit Another Application
      </button>
    </div>
  );
}
