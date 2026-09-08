import {
  currencyFormatter,
  formatPercentFromFraction,
  formatPercentValue,
  formatMultiplier,
  hasValue,
} from "../utils/assessment";

export default function AssessmentMetrics({ application }) {
  return (
    <div className="assessment-metrics-grid">
      {hasValue(application.interest_rate) && (
        <div className="metric-tile">
          <span className="metric-tile-label">Indicative Interest Rate</span>
          <span className="metric-tile-value">
            {formatPercentFromFraction(application.interest_rate)}
          </span>
        </div>
      )}

      {hasValue(application.emi) && (
        <div className="metric-tile">
          <span className="metric-tile-label">Monthly EMI</span>
          <span className="metric-tile-value">
            {currencyFormatter.format(application.emi)}
          </span>
        </div>
      )}

      {hasValue(application.foir) && (
        <div className="metric-tile">
          <span className="metric-tile-label">FOIR</span>
          <span className="metric-tile-value">
            {formatPercentValue(application.foir)}
          </span>
        </div>
      )}

      {hasValue(application.lti) && (
        <div className="metric-tile">
          <span className="metric-tile-label">LTI</span>
          <span className="metric-tile-value">
            {formatMultiplier(application.lti)}
          </span>
        </div>
      )}
    </div>
  );
}
