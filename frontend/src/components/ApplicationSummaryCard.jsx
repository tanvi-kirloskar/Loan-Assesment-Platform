import { LOAN_PURPOSE_OPTIONS } from "./LoanApplicationForm";
import { currencyFormatter, hasValue } from "../utils/assessment";

function purposeLabel(value) {
  const match = LOAN_PURPOSE_OPTIONS.find((option) => option.value === value);
  return match ? match.label : value;
}

export default function ApplicationSummaryCard({
  application,
  onSelect,
  isLatest = false,
}) {
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
        <div className="summary-card-heading">
          <span className="summary-card-id">
            Application #{application.id}
            {isLatest && <span className="summary-latest-tag">Latest</span>}
          </span>
          <span className="summary-card-purpose">
            {purposeLabel(application.loan_purpose)} Loan
          </span>
        </div>
        <span className="summary-decision-badge">{decision || "PENDING"}</span>
      </div>

      <p className="summary-card-amount">
        {currencyFormatter.format(application.loan_amount)}
      </p>

      {(hasValue(application.interest_rate) ||
        hasValue(application.emi) ||
        hasValue(application.foir) ||
        hasValue(application.lti)) && (
        <div className="summary-card-metrics">
          {hasValue(application.interest_rate) && (
            <span>
              <strong>{(application.interest_rate * 100).toFixed(2)}%</strong>{" "}
              rate
            </span>
          )}
          {hasValue(application.emi) && (
            <span>
              <strong>{currencyFormatter.format(application.emi)}</strong> EMI
            </span>
          )}
          {hasValue(application.foir) && (
            <span>
              <strong>{application.foir.toFixed(2)}%</strong> FOIR
            </span>
          )}
          {hasValue(application.lti) && (
            <span>
              <strong>{application.lti.toFixed(2)}×</strong> LTI
            </span>
          )}
        </div>
      )}

      <span className="summary-card-view">View application →</span>
    </button>
  );
}
