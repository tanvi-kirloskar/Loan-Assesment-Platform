import { useEffect, useMemo, useState } from "react";
import {
  getAdvisorApplication,
  getAdvisorWorkflow,
  getAdvisorAudit,
  submitAdvisorDecision,
  requestAdvisorInfo,
  ApiError,
} from "../services/api";
import { formatPercentFromFraction } from "../utils/assessment";

function money(value) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value));
}

function dateTime(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function label(value) {
  return value ? String(value).replaceAll("_", " ") : "—";
}

function decisionClass(value) {
  return String(value || "").toLowerCase();
}

function Metric({ label: title, value, suffix = "" }) {
  return (
    <div className="advisor-metric">
      <span>{title}</span>
      <strong>{value === null || value === undefined ? "—" : `${value}${suffix}`}</strong>
    </div>
  );
}

function FoirChart({ value }) {
  const numeric = Number(value || 0);
  const width = Math.min(Math.max(numeric, 0), 100);
  return (
    <div className="advisor-chart-card">
      <div className="advisor-chart-title"><span>FOIR</span><strong>{numeric.toFixed(1)}%</strong></div>
      <div className="foir-track">
        <span className="foir-fill" style={{ width: `${width}%` }} />
        <span className="foir-threshold" style={{ left: "50%" }}><i /></span>
      </div>
      <div className="chart-scale"><span>0%</span><span>Configured limit 50%</span><span>100%</span></div>
    </div>
  );
}

function IncomeAllocation({ income, existingEmi, newEmi }) {
  const totalIncome = Number(income || 0);
  const existing = Math.max(Number(existingEmi || 0), 0);
  const proposed = Math.max(Number(newEmi || 0), 0);
  const total = existing + proposed;
  const remaining = Math.max(totalIncome - total, 0);
  const base = totalIncome || 1;
  return (
    <div className="advisor-chart-card">
      <div className="advisor-chart-title"><span>Monthly income allocation</span><strong>{money(remaining)} remaining</strong></div>
      <div className="allocation-track">
        <span className="allocation-existing" style={{ width: `${Math.min(existing / base * 100, 100)}%` }} />
        <span className="allocation-proposed" style={{ width: `${Math.min(proposed / base * 100, 100)}%` }} />
      </div>
      <div className="allocation-legend">
        <span><i className="legend-existing" /> Existing EMI {money(existing)}</span>
        <span><i className="legend-proposed" /> New EMI {money(proposed)}</span>
        <span><i className="legend-remaining" /> Remaining {money(remaining)}</span>
      </div>
    </div>
  );
}

function RiskChart({ score, factors }) {
  const safeScore = Math.min(Math.max(Number(score || 0), 0), 100);
  return (
    <div className="advisor-risk-card">
      <div className="advisor-risk-heading">
        <div><span className="advisor-section-kicker">Review risk</span><h3>{safeScore}<small>/100</small></h3></div>
        <span className="advisor-risk-note">Deterministic workflow signal</span>
      </div>
      <div className="risk-large-track"><span style={{ width: `${safeScore}%` }} /></div>
      {factors?.length ? (
        <ul className="risk-factor-list">
          {factors.map((factor) => <li key={`${factor.code}-${factor.points}`}><span>{factor.label}</span><strong>+{factor.points}</strong></li>)}
        </ul>
      ) : <p className="advisor-muted">No review-risk factors were detected.</p>}
    </div>
  );
}

export default function AdvisorReview({ applicationId, onBack, onSessionExpired }) {
  const [application, setApplication] = useState(null);
  const [workflow, setWorkflow] = useState(null);
  const [audit, setAudit] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState(null);
  const [notes, setNotes] = useState("");
  const [actionMessage, setActionMessage] = useState(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const [detail, workflowData, auditData] = await Promise.all([
        getAdvisorApplication(applicationId),
        getAdvisorWorkflow(applicationId),
        getAdvisorAudit(applicationId),
      ]);
      setApplication(detail);
      setWorkflow(workflowData);
      setAudit(auditData);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }
      setError(err instanceof ApiError ? err.message : "Could not load this application.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, [applicationId]);

  async function handleDecision(action) {
    if (!notes.trim()) {
      setActionMessage("Add an advisor rationale before recording a decision.");
      return;
    }
    setActionLoading(true);
    setActionMessage(null);
    try {
      if (action === "REQUEST_INFO") {
        await requestAdvisorInfo(applicationId, notes.trim());
      } else {
        await submitAdvisorDecision(applicationId, action, notes.trim());
      }
      setNotes("");
      setActionMessage(`${label(action)} recorded successfully.`);
      await load();
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        onSessionExpired("Your session has expired. Please log in again.");
        return;
      }
      setActionMessage(err instanceof ApiError ? err.message : "Could not record the action.");
    } finally {
      setActionLoading(false);
    }
  }

  const income = application?.monthly_income;
  const existingEmi = application?.existing_monthly_emi;
  const newEmi = application?.emi;
  const reasons = application?.decision_reasons?.length
    ? application.decision_reasons
    : application?.assessment_reasons
      ? [application.assessment_reasons]
      : [];

  const latestRun = application?.verification_run;
  const findings = application?.findings || [];
  const documents = application?.documents || [];
  const evidence = application?.evidence || [];
  const policyEvidence = workflow?.policy_evidence || [];
  const riskFactors = workflow?.review_risk_factors || application?.review_risk_factors || [];
  const riskScore = workflow?.review_risk_score ?? application?.review_risk_score ?? 0;

  const evidenceByDocument = useMemo(() => {
    const map = new Map();
    evidence.forEach((item) => {
      if (!map.has(item.document_id)) map.set(item.document_id, []);
      map.get(item.document_id).push(item);
    });
    return map;
  }, [evidence]);

  if (loading) return <div className="advisor-shell"><p className="advisor-state">Loading review workspace…</p></div>;
  if (error) return <div className="advisor-shell"><div className="advisor-error">{error}</div><button type="button" className="advisor-secondary-button" onClick={load}>Retry</button></div>;
  if (!application) return null;

  return (
    <div className="advisor-shell">
      <header className="advisor-review-header">
        <button type="button" className="advisor-back-button" onClick={onBack}>← Back to Applications</button>
        <div className="advisor-review-title">
          <div>
            <p className="advisor-section-kicker">Application #{application.id}</p>
            <h1>{application.applicant_name}</h1>
            <p>{label(application.loan_purpose)} · {money(application.loan_amount)} · {application.loan_tenure_months} months</p>
          </div>
          <div className="advisor-review-badges">
            <span className={`advisor-badge ${decisionClass(application.decision)}`}>D3 {label(application.decision)}</span>
            <span className="advisor-status">{label(application.status)}</span>
            <span className="advisor-route">{label(application.verification_route)}</span>
          </div>
        </div>
      </header>

      <section className="advisor-metrics-grid">
        <Metric label="Monthly income" value={money(income)} />
        <Metric label="Existing EMI" value={money(existingEmi)} />
        <Metric label="Loan amount" value={money(application.loan_amount)} />
        <Metric label="New EMI" value={money(newEmi)} />
        <Metric label="FOIR" value={application.foir} suffix="%" />
        <Metric label="LTI" value={application.lti} />
        <Metric label="Credit score" value={application.credit_score} />
        <Metric
          label="Interest rate"
          value={
            application.interest_rate !== null && application.interest_rate !== undefined
              ? formatPercentFromFraction(application.interest_rate)
              : null
          }
        />
      </section>

      <main className="advisor-review-grid">
        <section className="advisor-panel">
          <div className="advisor-panel-heading"><div><span className="advisor-section-kicker">Evidence</span><h2>Documents</h2></div></div>
          <div className="advisor-document-list">
            {documents.length ? documents.map((doc) => (
              <article className={`advisor-document ${doc.is_active ? "active" : ""}`} key={String(doc.id)}>
                <div>
                  <strong>{label(doc.document_type)}</strong>
                  <p>{doc.original_filename}</p>
                </div>
                <div className="advisor-document-meta">
                  <span>v{doc.version_number}</span>
                  <span>{doc.is_active ? "Active" : "Historical"}</span>
                </div>
                {evidenceByDocument.get(doc.id)?.length ? (
                  <div className="advisor-evidence-list">
                    {evidenceByDocument.get(doc.id).map((item) => (
                      <div key={String(item.id)}><span>{label(item.field_name)}</span><strong>{item.extracted_value}</strong>{item.confidence != null && <em>{Math.round(Number(item.confidence) * 100)}%</em>}</div>
                    ))}
                  </div>
                ) : null}
              </article>
            )) : <p className="advisor-muted">No documents attached.</p>}
          </div>
        </section>

        <section className="advisor-panel">
          <div className="advisor-panel-heading"><div><span className="advisor-section-kicker">Deterministic assessment</span><h2>Financial Assessment</h2></div><span className={`advisor-badge ${decisionClass(application.decision)}`}>{label(application.decision)}</span></div>
          <div className="advisor-assessment-reasons">
            <h3>Why?</h3>
            {reasons.length ? <ul>{reasons.map((reason, index) => <li key={`${reason}-${index}`}>{reason}</li>)}</ul> : <p>No rejection/approval reasons were recorded.</p>}
          </div>
          <FoirChart value={application.foir} />
          <IncomeAllocation income={income} existingEmi={existingEmi} newEmi={newEmi} />
        </section>

        <section className="advisor-panel advisor-panel-right">
          <RiskChart score={riskScore} factors={riskFactors} />
          <div className="advisor-issues">
            <div className="advisor-panel-heading"><div><span className="advisor-section-kicker">Verification</span><h2>Key Issues</h2></div></div>
            {findings.length ? (
              <div className="advisor-findings">
                {findings.map((finding) => <article key={String(finding.id)} className={`finding-${String(finding.severity).toLowerCase()}`}><div><strong>{label(finding.finding_type)}</strong><span>{label(finding.action)}</span></div><p>{finding.message}</p></article>)}
              </div>
            ) : <p className="advisor-muted">No verification findings in the latest run.</p>}
          </div>
          <div className="advisor-workflow-block">
            <div className="advisor-panel-heading"><div><span className="advisor-section-kicker">Policy + AI</span><h2>Advisory Context</h2></div></div>
            <div className="advisor-ai-box"><strong>AI explanation</strong><p>{workflow?.ai_explanation || "No explanation available."}</p></div>
            {policyEvidence.length ? policyEvidence.map((item, index) => (
              <details className="advisor-policy" key={`${item.source}-${item.section}-${index}`}>
                <summary>{item.section}</summary><p>{item.content}</p><small>{item.source}</small>
              </details>
            )) : <p className="advisor-muted">No policy evidence was returned.</p>}
          </div>
        </section>
      </main>

      <section className="advisor-lower-grid">
        <div className="advisor-panel advisor-decision-panel">
          <div className="advisor-panel-heading"><div><span className="advisor-section-kicker">Human review</span><h2>Advisor Decision</h2></div></div>
          <p className="advisor-muted">D3 remains deterministic. Your action records the human workflow decision and rationale.</p>
          <textarea value={notes} onChange={(event) => setNotes(event.target.value)} placeholder="Enter rationale or information requested…" rows={4} />
          <div className="advisor-action-row">
            <button type="button" className="advisor-action advisor-request" disabled={actionLoading} onClick={() => handleDecision("REQUEST_INFO")}>Request Info</button>
            <button type="button" className="advisor-action advisor-reject" disabled={actionLoading} onClick={() => handleDecision("REJECT")}>Reject</button>
            <button type="button" className="advisor-action advisor-approve" disabled={actionLoading} onClick={() => handleDecision("APPROVE")}>Approve</button>
          </div>
          {actionMessage && <p className="advisor-action-message">{actionMessage}</p>}
        </div>

        <div className="advisor-panel">
          <div className="advisor-panel-heading"><div><span className="advisor-section-kicker">History</span><h2>Audit History</h2></div></div>
          {audit.length ? <div className="advisor-timeline">{audit.map((event) => <article key={String(event.id)}><span className="timeline-dot" /><div><strong>{label(event.action)}</strong><p>{event.notes || "No note recorded."}</p><small>{dateTime(event.created_at)} · {event.actor_role}</small></div></article>)}</div> : <p className="advisor-muted">No audit events yet.</p>}
        </div>
      </section>

      <section className="advisor-panel">
        <div className="advisor-panel-heading"><div><span className="advisor-section-kicker">Verification</span><h2>Verification History</h2></div><span>{latestRun ? `Current run #${latestRun.run_number}` : "No run"}</span></div>
        <div className="advisor-run-grid">
          {(application.verification_history || []).map((run) => (
            <div key={String(run.id)} className={`advisor-run ${run.is_latest ? "latest" : ""}`}>
              <strong>Run #{run.run_number}</strong>
              <span>{label(run.status)}</span>
              <small>{run.is_latest ? "Current" : "Historical"} · {dateTime(run.created_at)}</small>
              {run.completed_at && <small>Completed {dateTime(run.completed_at)}</small>}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
