import { useState } from "react";
import LoanApplicationForm from "./components/LoanApplicationForm";
import ResultCard from "./components/ResultCard";
import { createApplication, ApiError } from "./services/api";
import "./App.css";

export default function App() {
  const [submittedApplication, setSubmittedApplication] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  async function handleSubmit(payload) {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const application = await createApplication(payload);
      setSubmittedApplication(application);
    } catch (error) {
      if (error instanceof ApiError) {
        setSubmitError(error.message);
      } else {
        setSubmitError("An unexpected error occurred. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleReset() {
    setSubmittedApplication(null);
    setSubmitError(null);
  }

  return (
    <div className="page">
      <div className="app-shell">
        <header className="app-header">
          <h1>Loan Assessment &amp; Advisory Platform</h1>
          <p>
            Submit your details below for an instant, policy-based loan
            assessment.
          </p>
        </header>

        <main className="app-card">
          {submittedApplication ? (
            <ResultCard
              application={submittedApplication}
              onReset={handleReset}
            />
          ) : (
            <>
              {submitError && (
                <div className="submit-error" role="alert">
                  {submitError}
                </div>
              )}
              <LoanApplicationForm
                onSubmit={handleSubmit}
                isSubmitting={isSubmitting}
              />
            </>
          )}
        </main>
      </div>
    </div>
  );
}
