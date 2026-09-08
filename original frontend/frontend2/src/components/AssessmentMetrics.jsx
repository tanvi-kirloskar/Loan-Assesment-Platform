import {
  currencyFormatter,
  formatPercentFromFraction,
  formatPercentValue,
  formatMultiplier,
  hasValue,
} from "../utils/assessment";

export default function AssessmentMetrics({ application }) {
  return (
    <div className="assessment-metrics">
      {hasValue(application.interest_rate) && (
        <div className="result-row">
          <span className="result-label">Interest Rate</span>
          <span className="result-value">
            {formatPercentFromFraction(application.interest_rate)}
          </span>
        </div>
      )}

      {hasValue(application.emi) && (
        <div className="result-row">
          <span className="result-label">Monthly EMI</span>
          <span className="result-value">
            {currencyFormatter.format(application.emi)}
          </span>
        </div>
      )}

      {hasValue(application.foir) && (
        <div className="result-row">
          <span className="result-label">FOIR</span>
          <span className="result-value">
            {formatPercentValue(application.foir)}
          </span>
        </div>
      )}

      {hasValue(application.lti) && (
        <div className="result-row">
          <span className="result-label">LTI</span>
          <span className="result-value">
            {formatMultiplier(application.lti)}
          </span>
        </div>
      )}
    </div>
  );
}
