import ApplicationSummaryCard from "./ApplicationSummaryCard";

export default function Dashboard({
  applications = [],
  isLoading = false,
  error = null,
  onStartNewApplication,
  onSelectApplication,
  onLogout,
}) {
  const hasApplications = applications.length > 0;

  return (
    <div className="page">
      <div className="app-shell">
        <header className="app-header">
          <div className="app-header-row">
            <div>
              <h1>Loan Assessment &amp; Advisory Platform</h1>
              <p>Track your loan applications and assessment results.</p>
            </div>
            <button type="button" className="logout-link" onClick={onLogout}>
              Log out
            </button>
          </div>
        </header>

        <div className="dashboard-intro">
          <p className="dashboard-welcome">Welcome back</p>
          <button
            type="button"
            className="submit-button dashboard-cta"
            onClick={onStartNewApplication}
          >
            Start New Application
          </button>
        </div>

        <section className="dashboard-applications">
          <h2 className="dashboard-section-heading">Your Applications</h2>

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
                />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
