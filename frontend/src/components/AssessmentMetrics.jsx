import {
  currencyFormatter,
  formatPercentFromFraction,
  formatPercentValue,
  formatMultiplier,
  hasValue,
} from "../utils/assessment";

export default function AssessmentMetrics({ application }) {
  return (
    <div className="assessment-metrics-wrap">
      <div className="assessment-metrics-grid">
        {hasValue(application.emi) && (
          <div className="metric-tile">
            <span className="metric-tile-value">
              {currencyFormatter.format(application.emi)}
            </span>
            <span className="metric-tile-label">Estimated Monthly EMI</span>
          </div>
        )}

        {hasValue(application.interest_rate) && (
          <div className="metric-tile">
            <span className="metric-tile-value">
              {formatPercentFromFraction(application.interest_rate)}
            </span>
            <span className="metric-tile-label">Indicative Interest Rate</span>
          </div>
        )}
      </div>

      {(hasValue(application.foir) || hasValue(application.lti)) && (
        <div className="assessment-metrics-secondary">
          {hasValue(application.foir) && (
            <div className="result-row">
              <span className="result-label">
                <abbr
                  className="metric-tile-abbr"
                  title="Fixed Obligation to Income Ratio — the share of your monthly income already committed to existing and proposed loan repayments."
                >
                  FOIR
                </abbr>
              </span>
              <span className="result-value">
                {formatPercentValue(application.foir)}
              </span>
            </div>
          )}

          {hasValue(application.lti) && (
            <div className="result-row">
              <span className="result-label">
                <abbr
                  className="metric-tile-abbr"
                  title="Loan-to-Income — the loan amount expressed as a multiple of your monthly income."
                >
                  LTI
                </abbr>
              </span>
              <span className="result-value">
                {formatMultiplier(application.lti)}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
