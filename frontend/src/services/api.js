const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * Thrown for any non-network failure so callers can distinguish
 * "server responded with an error" from "request never reached the server".
 */
export class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

/**
 * Submits a new loan application.
 * @param {{ full_name: string, monthly_income: number, loan_amount: number, loan_tenure_months: number }} payload
 * @returns {Promise<{ id: number, full_name: string, monthly_income: number, loan_amount: number, loan_tenure_months: number, status: string }>}
 */
export async function createApplication(payload) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/applications`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
  } catch (networkError) {
    throw new ApiError(
      "Could not reach the server. Check that the backend is running and try again.",
      null,
      networkError
    );
  }

  if (!response.ok) {
    let details = null;
    try {
      details = await response.json();
    } catch {
      // response body wasn't JSON — ignore, we still have the status code
    }

    if (response.status === 422) {
      throw new ApiError(
        "The application couldn't be validated. Please check the values you entered.",
        response.status,
        details
      );
    }

    throw new ApiError(
      "Something went wrong on the server while submitting your application.",
      response.status,
      details
    );
  }

  return response.json();
}

/**
 * Fetches a previously submitted application by id.
 * @param {number} applicationId
 */
export async function getApplication(applicationId) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/applications/${applicationId}`);
  } catch (networkError) {
    throw new ApiError(
      "Could not reach the server. Check that the backend is running and try again.",
      null,
      networkError
    );
  }

  if (response.status === 404) {
    throw new ApiError("No application found with that ID.", 404);
  }

  if (!response.ok) {
    throw new ApiError(
      "Something went wrong on the server while fetching the application.",
      response.status
    );
  }

  return response.json();
}
