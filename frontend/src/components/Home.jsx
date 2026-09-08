export default function Home({ onGetStarted, onSignIn }) {
  return (
    <div className="page">
      <div className="home-shell">
        <section className="home-hero">
          <h1>Loan Assessment &amp; Advisory Platform</h1>
          <p className="home-tagline">
            Transparent, policy-based loan assessment.
          </p>
          <p className="home-description">
            Understand your loan application through structured financial
            assessment and clearly presented outcomes.
          </p>

          <div className="home-cta-row">
            <button
              type="button"
              className="submit-button home-cta"
              onClick={onGetStarted}
            >
              Get Started
            </button>
            <p className="home-signin-line">
              Already have an account?{" "}
              <button type="button" className="auth-switch-link" onClick={onSignIn}>
                Sign in
              </button>
            </p>
          </div>
        </section>

        <section className="home-features">
          <div className="feature-card">
            <h3>Structured Assessment</h3>
            <p>
              Applications are evaluated using defined financial assessment
              criteria.
            </p>
          </div>
          <div className="feature-card">
            <h3>Transparent Outcomes</h3>
            <p>
              View the financial metrics contributing to the assessment
              outcome.
            </p>
          </div>
          <div className="feature-card">
            <h3>Application History</h3>
            <p>
              Track submitted applications and review previous assessment
              results.
            </p>
          </div>
        </section>

        <section className="home-how-it-works">
          <h2 className="dashboard-section-heading">How it works</h2>
          <div className="how-steps">
            <div className="how-step">
              <span className="how-step-number">01</span>
              <p>Submit your financial details</p>
            </div>
            <div className="how-step">
              <span className="how-step-number">02</span>
              <p>Receive a policy-based assessment</p>
            </div>
            <div className="how-step">
              <span className="how-step-number">03</span>
              <p>Review your assessment outcome</p>
            </div>
            <div className="how-step">
              <span className="how-step-number">04</span>
              <p>Track your applications</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
