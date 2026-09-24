import { useState, useEffect, useCallback } from "react";
import Home from "./components/Home";
import AuthForm from "./components/AuthForm";
import LoanApplicationForm from "./components/LoanApplicationForm";
import AssessmentResult from "./components/AssessmentResult";
import Dashboard from "./components/Dashboard";
import ApplicationDetail from "./components/ApplicationDetail";
import {
  createApplication,
  getApplication,
  listApplications,
  listAdvisorApplications,
  getAccessToken,
  getUserRole,
  clearAccessToken,
  ApiError,
} from "./services/api";
import "./App.css";
import "./Advisor.css";
import AdvisorDashboard from "./components/AdvisorDashboard";
import AdvisorReview from "./components/AdvisorReview";

// view is one of: "home" | "auth" | "dashboard" | "newApplication" | "result" | "detail"

export default function App() {
  const [view, setView] = useState(() => {
    if (getAccessToken() === null) return "home";
    return getUserRole() === "ADVISOR" ? "advisorDashboard" : "dashboard";
  });
  const [authInitialMode, setAuthInitialMode] = useState("login");
  const [authNotice, setAuthNotice] = useState(null);

  const [applications, setApplications] = useState([]);
  const [isLoadingApplications, setIsLoadingApplications] = useState(false);
  const [applicationsError, setApplicationsError] = useState(null);
  const [advisorApplications, setAdvisorApplications] = useState([]);
  const [isLoadingAdvisor, setIsLoadingAdvisor] = useState(false);
  const [advisorError, setAdvisorError] = useState(null);
  const [advisorApplicationId, setAdvisorApplicationId] = useState(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  const [lastSubmittedApplication, setLastSubmittedApplication] =
    useState(null);

  const [selectedApplication, setSelectedApplication] = useState(null);
  const [detailApplicationId, setDetailApplicationId] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState(null);

  // Central place to react to an expired/invalid session: clear the token,
  // drop every screen-specific state, and send the user back to AuthForm
  // with an explanation instead of silently dropping them there.
  const handleSessionExpired = useCallback((message) => {
    clearAccessToken();
    setView("auth");
    setAuthNotice(message);
    setApplications([]);
    setLastSubmittedApplication(null);
    setSelectedApplication(null);
  }, []);

  const loadApplications = useCallback(async () => {
    setIsLoadingApplications(true);
    setApplicationsError(null);

    try {
      const data = await listApplications();
      setApplications(data);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        handleSessionExpired("Your session has expired. Please log in again.");
        return;
      }
      setApplicationsError(
        error instanceof ApiError
          ? error.message
          : "An unexpected error occurred. Please try again."
      );
    } finally {
      setIsLoadingApplications(false);
    }
  }, [handleSessionExpired]);

  // Dashboard always reflects GET /applications, so load it on mount if
  // already authenticated, and every time the app navigates back to it.
  useEffect(() => {
    if (view === "dashboard") {
      loadApplications();
    }
    if (view === "advisorDashboard") {
      setIsLoadingAdvisor(true);
      setAdvisorError(null);
      listAdvisorApplications()
        .then(setAdvisorApplications)
        .catch((error) => {
          if (error instanceof ApiError && error.status === 401) {
            handleSessionExpired("Your session has expired. Please log in again.");
            return;
          }
          setAdvisorError(
            error instanceof ApiError
              ? error.message
              : "Could not load advisor applications."
          );
        })
        .finally(() => {
          setIsLoadingAdvisor(false);
        });
    }
  }, [view, loadApplications, handleSessionExpired]);

  function handleAuthSuccess() {
    setAuthNotice(null);
    setView(getUserRole() === "ADVISOR" ? "advisorDashboard" : "dashboard");
  }

  function handleLogout() {
    clearAccessToken();
    setView("home");
    setAuthNotice(null);
    setApplications([]);
    setLastSubmittedApplication(null);
    setSelectedApplication(null);
  }

  function handleGetStarted() {
    setAuthInitialMode("register");
    setView("auth");
  }

  function handleSignIn() {
    setAuthInitialMode("login");
    setView("auth");
  }

  function handleStartNewApplication() {
    setSubmitError(null);
    setView("newApplication");
  }

  async function handleSubmitApplication(payload) {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const application = await createApplication(payload);
      setLastSubmittedApplication(application);
      setView("result");
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        handleSessionExpired("Your session has expired. Please log in again.");
        return;
      }
      setSubmitError(
        error instanceof ApiError
          ? error.message
          : "An unexpected error occurred. Please try again."
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleSubmitAnother() {
    setLastSubmittedApplication(null);
    setSubmitError(null);
    setView("newApplication");
  }

  function handleBackToDashboard() {
    setLastSubmittedApplication(null);
    setSelectedApplication(null);
    setDetailApplicationId(null);
    setDetailError(null);
    setView("dashboard");
  }

  async function handleSelectApplication(applicationId) {
    setView("detail");
    setSelectedApplication(null);
    setDetailApplicationId(applicationId);
    setIsLoadingDetail(true);
    setDetailError(null);

    try {
      const application = await getApplication(applicationId);
      setSelectedApplication(application);
    } catch (error) {
      if (error instanceof ApiError && error.status === 401) {
        handleSessionExpired("Your session has expired. Please log in again.");
        return;
      }
      setDetailError(
        error instanceof ApiError
          ? error.message
          : "An unexpected error occurred. Please try again."
      );
    } finally {
      setIsLoadingDetail(false);
    }
  }

  function handleRetryDetail() {
    if (detailApplicationId !== null) {
      handleSelectApplication(detailApplicationId);
    }
  }

  if (view === "home") {
    return <Home onGetStarted={handleGetStarted} onSignIn={handleSignIn} />;
  }

  if (view === "auth") {
    return (
      <div className="page">
        <div className="app-shell">
          <header className="app-header">
            <div>
              <h1>Loan Assessment &amp; Advisory Platform</h1>
              <p>Log in or create an account to start a loan application.</p>
            </div>
          </header>
          <AuthForm
            onAuthSuccess={handleAuthSuccess}
            notice={authNotice}
            initialMode={authInitialMode}
          />
        </div>
      </div>
    );
  }

  if (view === "dashboard") {
    return (
      <Dashboard
        applications={applications}
        isLoading={isLoadingApplications}
        error={applicationsError}
        onStartNewApplication={handleStartNewApplication}
        onSelectApplication={handleSelectApplication}
        onLogout={handleLogout}
      />
    );
  }

  if (view === "newApplication") {
    return (
      <div className="page">
        <div className="form-shell">
          <header className="app-header">
            <div className="app-header-row">
              <div>
                <h1>Loan Assessment &amp; Advisory Platform</h1>
                <p>
                  Submit your details below for an instant, policy-based loan
                  assessment.
                </p>
              </div>
              <button
                type="button"
                className="logout-link"
                onClick={handleBackToDashboard}
              >
                Cancel
              </button>
            </div>
          </header>

          <main className="app-card">
            {submitError && (
              <div className="submit-error" role="alert">
                {submitError}
              </div>
            )}
            <LoanApplicationForm
              onSubmit={handleSubmitApplication}
              isSubmitting={isSubmitting}
            />
          </main>
        </div>
      </div>
    );
  }

  if (view === "result") {
    return (
      <div className="page">
        <div className="app-shell">
          <header className="app-header">
            <h1>Loan Assessment &amp; Advisory Platform</h1>
          </header>
          <main className="app-card">
            <AssessmentResult
              application={lastSubmittedApplication}
              onReset={handleSubmitAnother}
              onBackToDashboard={handleBackToDashboard}
            />
          </main>
        </div>
      </div>
    );
  }

  if (view === "detail") {
    return (
      <div className="page">
        <div className="dashboard-shell">
          <header className="app-header">
            <h1>Loan Assessment &amp; Advisory Platform</h1>
          </header>
          <main className="app-card">
            {isLoadingDetail && (
              <p className="dashboard-status-text">
                Loading application details…
              </p>
            )}
            {!isLoadingDetail && detailError && (
              <>
                <div className="submit-error" role="alert">
                  {detailError}
                </div>
                <div className="detail-error-actions">
                  <button
                    type="button"
                    className="submit-button"
                    onClick={handleRetryDetail}
                  >
                    Retry
                  </button>
                  <button
                    type="button"
                    className="secondary-button"
                    onClick={handleBackToDashboard}
                  >
                    Back to Dashboard
                  </button>
                </div>
              </>
            )}
            {!isLoadingDetail && !detailError && selectedApplication && (
              <ApplicationDetail
                application={selectedApplication}
                onBack={handleBackToDashboard}
                onSessionExpired={handleSessionExpired}
                onResubmitted={() => {
                  if (detailApplicationId !== null) {
                    handleSelectApplication(detailApplicationId);
                  }
                }}
              />
            )}
          </main>
        </div>
      </div>
    );
  }

  if (view === "advisorDashboard") {
    return (
      <AdvisorDashboard
        applications={advisorApplications}
        isLoading={isLoadingAdvisor}
        error={advisorError}
        onSelectApplication={(id) => {
          setAdvisorApplicationId(id);
          setView("advisorReview");
        }}
        onLogout={handleLogout}
      />
    );
  }

  if (view === "advisorReview" && advisorApplicationId !== null) {
    return (
      <AdvisorReview
        applicationId={advisorApplicationId}
        onBack={() => setView("advisorDashboard")}
        onSessionExpired={handleSessionExpired}
      />
    );
  }

  return null;
}
