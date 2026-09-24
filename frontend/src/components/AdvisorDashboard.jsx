import { useMemo, useState } from "react";

function formatCurrency(value) {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(Number(value));
}

function decisionLabel(value) {
  return value ? String(value).replaceAll("_", " ") : "Pending";
}

export default function AdvisorDashboard({
  applications,
  isLoading,
  error,
  onSelectApplication,
  onLogout,
}) {
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");

  const counts = useMemo(() => {
    const rows = applications || [];
    return {
      total: rows.length,
      review: rows.filter(
        (row) =>
          (row.status === "submitted" && !row.decision) ||
          row.status === "resubmitted"
      ).length,
      resubmitted: rows.filter((row) => row.status === "resubmitted").length,
      info: rows.filter((row) => row.status === "information_requested").length,
      approved: rows.filter(
        (row) => row.status === "approved" || row.decision === "APPROVED"
      ).length,
      rejected: rows.filter(
        (row) => row.status === "rejected" || row.decision === "REJECTED"
      ).length,
    };
  }, [applications]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return (applications || []).filter((row) => {
      const matchesQuery =
        !q ||
        String(row.id).includes(q) ||
        String(row.applicant_name || "").toLowerCase().includes(q);
      const matchesStatus =
        statusFilter === "ALL" || row.status === statusFilter;
      return matchesQuery && matchesStatus;
    });
  }, [applications, query, statusFilter]);

  return (
    <div className="advisor-shell">
      <header className="advisor-topbar">
        <div>
          <p className="advisor-eyebrow">Advisor Workspace</p>
          <h1>Loan review queue</h1>
          <p className="advisor-subtitle">
            Triage applications, inspect evidence, and make auditable decisions.
          </p>
        </div>
        <button type="button" className="advisor-ghost-button" onClick={onLogout}>
          Log out
        </button>
      </header>

      <section className="advisor-kpis" aria-label="Application summary">
        <div className="advisor-kpi"><span>Total Applications</span><strong>{counts.total}</strong></div>
        <div className="advisor-kpi advisor-kpi-attention"><span>Needs Review</span><strong>{counts.review}</strong></div>
        <div className="advisor-kpi"><span>Resubmitted</span><strong>{counts.resubmitted}</strong></div>
        <div className="advisor-kpi"><span>Information Requested</span><strong>{counts.info}</strong></div>
        <div className="advisor-kpi advisor-kpi-approved"><span>Approved</span><strong>{counts.approved}</strong></div>
        <div className="advisor-kpi advisor-kpi-rejected"><span>Rejected</span><strong>{counts.rejected}</strong></div>
      </section>

      <section className="advisor-queue">
        <div className="advisor-section-header">
          <div>
            <p className="advisor-section-kicker">Review queue</p>
            <h2>Applications</h2>
          </div>
          <div className="advisor-filters">
            <label>
              <span className="sr-only">Search applications</span>
              <input
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search ID or applicant"
                className="advisor-search"
              />
            </label>
            <select
              value={statusFilter}
              onChange={(event) => setStatusFilter(event.target.value)}
              className="advisor-filter"
              aria-label="Filter by status"
            >
              <option value="ALL">All statuses</option>
              <option value="submitted">Submitted</option>
              <option value="resubmitted">Resubmitted</option>
              <option value="information_requested">Information requested</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
            </select>
          </div>
        </div>

        {isLoading && <p className="advisor-state">Loading applications…</p>}
        {error && <div className="advisor-error" role="alert">{error}</div>}

        {!isLoading && !error && (
          <div className="advisor-table-wrap">
            <table className="advisor-table">
              <thead>
                <tr>
                  <th>Application</th>
                  <th>Applicant</th>
                  <th>Loan Amount</th>
                  <th>D3 Decision</th>
                  <th>Review Risk</th>
                  <th>FOIR</th>
                  <th>LTI</th>
                  <th>Status</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                {filtered.map((row) => (
                  <tr key={row.id} onClick={() => onSelectApplication(row.id)}>
                    <td className="advisor-primary-cell">#{row.id}</td>
                    <td>{row.applicant_name || "—"}</td>
                    <td>{formatCurrency(row.loan_amount)}</td>
                    <td>
                      <span className={`advisor-badge ${String(row.decision || "").toLowerCase()}`}>
                        {decisionLabel(row.decision)}
                      </span>
                    </td>
                    <td>
                      <div className="risk-inline">
                        <span>{row.review_risk_score ?? 0}</span>
                        <span className="risk-track"><span style={{ width: `${Math.min(row.review_risk_score || 0, 100)}%` }} /></span>
                      </div>
                    </td>
                    <td>{row.foir == null ? "—" : `${Number(row.foir).toFixed(1)}%`}</td>
                    <td>{row.lti == null ? "—" : Number(row.lti).toFixed(2)}</td>
                    <td><span className="advisor-status">{decisionLabel(row.status)}</span></td>
                    <td><button type="button" className="advisor-open-button" onClick={(event) => { event.stopPropagation(); onSelectApplication(row.id); }}>Review →</button></td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filtered.length === 0 && <p className="advisor-state">No applications match the current filters.</p>}
          </div>
        )}
      </section>
    </div>
  );
}
