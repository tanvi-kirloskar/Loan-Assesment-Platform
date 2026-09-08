import { LOAN_PURPOSE_OPTIONS } from "./LoanApplicationForm";

const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

function purposeLabel(value) {
  const match = LOAN_PURPOSE_OPTIONS.find((option) => option.value === value);
  return match ? match.label : value;
}

function hasValue(value) {
  return value !== null && value !== undefined;
}

export default function ApplicationSummaryCard({ application, onSelect }) {
  const decision = (application.decision || "").toUpperCase();
  const isApproved = decision === "APPROVED";
  const isRejected = decision === "REJECTED";

  const decisionClass = isApproved
    ? "summary-approved"
    : isRejected
    ? "summary-rejected"
    : "summary-pending";

  return (
    <button
      type="button"
      className={`application-summary-card ${decisionClass}`}
      onClick={() => onSelect(application.id)}
    >
      <div className="summary-card-top">
        <span className="summary-card-id">Application #{application.id}</span>
        <span className="summary-decision-badge">{decision || "PENDING"}</span>
      </div>

      <div className="summary-card-details">
        <span className="summary-card-purpose">
          {purposeLabel(application.loan_purpose)}
        </span>
        <span className="summary-card-amount">
          {currencyFormatter.format(application.loan_amount)}
        </span>
      </div>

      {(hasValue(application.interest_rate) ||
        hasValue(application.emi) ||
        hasValue(application.foir) ||
        hasValue(application.lti)) && (
        <div className="summary-card-metrics">
          {hasValue(application.interest_rate) && (
            <span>{(application.interest_rate * 100).toFixed(2)}% rate</span>
          )}
          {hasValue(application.emi) && (
            <span>{currencyFormatter.format(application.emi)} EMI</span>
          )}
          {hasValue(application.foir) && (
            <span>{application.foir.toFixed(2)}% FOIR</span>
          )}
          {hasValue(application.lti) && (
            <span>{application.lti.toFixed(2)}× LTI</span>
          )}
        </div>
      )}

      <span className="summary-card-view">View details →</span>
    </button>
  );
}
