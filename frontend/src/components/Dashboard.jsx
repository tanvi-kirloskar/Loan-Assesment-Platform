import ApplicationSummaryCard from "./ApplicationSummaryCard";
import { summarizeApplications } from "../utils/assessment";

export default function Dashboard({
  applications = [],
  isLoading = false,
  error = null,
  onStartNewApplication,
  onSelectApplication,
  onLogout,
}) {
  const hasApplications = applications.length > 0;
  const { total, approved, rejected, latest } =
    summarizeApplications(applications);

  const latestDecisionLabel = latest
    ? (latest.decision || "Pending").toUpperCase()
    : "—";

  return (
    <div className="page">
      <div className="dashboard-shell">
        <header className="app-header">
          <div className="app-header-row">
            <div>
              <h1>Loan Assessment &amp; Advisory Platform</h1>
              <p className="account-strip">Signed in</p>
            </div>
            <button type="button" className="logout-link" onClick={onLogout}>
              Log out
            </button>
          </div>
        </header>

        <div className="dashboard-intro">
          <div>
            <p className="dashboard-welcome">Your loan overview</p>
            <p className="dashboard-subtitle">
              Track your loan applications and review each assessment result.
            </p>
          </div>
          <button
            type="button"
            className="submit-button dashboard-cta"
            onClick={onStartNewApplication}
          >
            + Start New Application
          </button>
        </div>

        {hasApplications && (
          <div className="overview-stats">
            <div className="stat-tile">
              <span className="stat-tile-label">Total Applications</span>
              <span className="stat-tile-value">{total}</span>
            </div>
            <div className="stat-tile">
              <span className="stat-tile-label">Approved</span>
              <span className="stat-tile-value stat-approved">
                {approved}
              </span>
            </div>
            <div className="stat-tile">
              <span className="stat-tile-label">Rejected</span>
              <span className="stat-tile-value stat-rejected">
                {rejected}
              </span>
            </div>
            <div className="stat-tile">
              <span className="stat-tile-label">Latest Assessment</span>
              <span className="stat-tile-value stat-tile-value-text">
                {latestDecisionLabel}
              </span>
            </div>
          </div>
        )}

        <section className="dashboard-applications">
          <h2 className="dashboard-section-heading">Applications</h2>

          {error && (
            <div className="submit-error" role="alert">
              {error}
            </div>
          )}

          {isLoading && (
            <p className="dashboard-status-text">Loading your applications…</p>
          )}

          {!isLoading && !error && !hasApplications && (
            <div className="empty-state">
              <p className="empty-state-heading">No applications yet</p>
              <p className="empty-state-text">
                Start your first loan application to receive a policy-based
                assessment.
              </p>
              <button
                type="button"
                className="submit-button"
                onClick={onStartNewApplication}
              >
                Start New Application
              </button>
            </div>
          )}

          {!isLoading && !error && hasApplications && (
            <div className="application-list">
              {applications.map((application) => (
                <ApplicationSummaryCard
                  key={application.id}
                  application={application}
                  onSelect={onSelectApplication}
                  isLatest={latest !== null && application.id === latest.id}
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
