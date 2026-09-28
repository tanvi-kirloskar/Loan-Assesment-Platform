import { useEffect, useState } from "react";
import AssessmentMetrics from "./AssessmentMetrics";
import DocumentsSection from "./DocumentsSection";
import { LOAN_PURPOSE_OPTIONS } from "./LoanApplicationForm";
import { currencyFormatter, getAssessmentReasons, hasValue } from "../utils/assessment";
import { getApplicationFindings, getInformationRequest, ApiError } from "../services/api";

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
  onResubmitted,
}) {
  const [findings, setFindings] = useState([]);
  const [informationRequest, setInformationRequest] = useState(null);
  const [workflowLoading, setWorkflowLoading] = useState(true);
  const [workflowError, setWorkflowError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    async function loadWorkflowDetails() {
      setWorkflowLoading(true);
      setWorkflowError(null);
      try {
        const [findingData, requestData] = await Promise.all([
          getApplicationFindings(application.id),
          getInformationRequest(application.id),
        ]);
        if (!cancelled) {
          setFindings(findingData || []);
          setInformationRequest(requestData);
        }
      } catch (error) {
        if (cancelled) return;
        if (error instanceof ApiError && error.status === 401) {
          onSessionExpired("Your session has expired. Please log in again.");
          return;
        }
        setWorkflowError(
          error instanceof ApiError
            ? error.message
            : "Could not load verification details."
        );
      } finally {
        if (!cancelled) setWorkflowLoading(false);
      }
    }
    loadWorkflowDetails();
    return () => { cancelled = true; };
  }, [application.id, onSessionExpired]);
  const decision = ["approved", "rejected"].includes(String(application.status || "").toLowerCase())
    ? (application.decision || "").toUpperCase()
    : "";
  const isApproved = decision === "APPROVED";
  const isRejected = decision === "REJECTED";
  const ruleDecision = String(application.assessment_decision || "").toUpperCase();
  const isRuleRejected = ruleDecision === "REJECTED";

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

      {application.status === "information_requested" && informationRequest && (
        <div className="information-request-banner" role="status">
          <strong>Action required: additional information requested</strong>
          <p>{informationRequest.notes}</p>
          <small>Requested {new Date(informationRequest.created_at).toLocaleString("en-IN")}</small>
        </div>
      )}

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
          <div className="detail-assessment-state">
            <span>Automated Rule Assessment</span>
            <strong className={ruleDecision === "REJECTED" ? "detail-rule-rejected" : "detail-rule-approved"}>
              {ruleDecision || "—"}
            </strong>
          </div>
          <p className="detail-assessment-note">This automated financial assessment is not the final advisor decision.</p>
          <AssessmentMetrics application={application} />

          {isRuleRejected && reasonItems.length > 0 && (
            <div className="assessment-reasons">
              <p className="assessment-reasons-heading">Automated Assessment Factors</p>
              <ul className="assessment-reasons-list">
                {reasonItems.map((reason, index) => <li key={index}>{reason}</li>)}
              </ul>
            </div>
          )}

          {false && (
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
        <div className="detail-assessment-heading-row">
          <h3 className="detail-section-heading">Verification Findings</h3>
          {!workflowLoading && <span className="detail-findings-count">{findings.length} finding{findings.length === 1 ? "" : "s"}</span>}
        </div>
        {workflowError && <div className="submit-error" role="alert">{workflowError}</div>}
        {workflowLoading ? (
          <p className="dashboard-status-text">Loading verification details…</p>
        ) : findings.length ? (
          <div className="applicant-findings">
            {findings.map((finding) => (
              <article className="applicant-finding" key={String(finding.id)}>
                <div><strong>{String(finding.finding_type).replaceAll("_", " ")}</strong><span>{String(finding.action).replaceAll("_", " ")}</span></div>
                <p>{finding.message}</p>
              </article>
            ))}
          </div>
        ) : (
          <p className="dashboard-status-text">No verification findings were recorded in the latest run.</p>
        )}
      </div>

      <div className="detail-section detail-section-full">
        <DocumentsSection
          applicationId={application.id}
          onSessionExpired={onSessionExpired}
          allowReplacement={application.status === "information_requested"}
          onResubmitted={onResubmitted}
        />
      </div>
    </div>
  );
}
