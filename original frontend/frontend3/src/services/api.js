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
 * Registers a new applicant account.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{ access_token: string, token_type: string }>}
 */
export async function register(email, password) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
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
      // Response body wasn't JSON.
    }

    throw new ApiError(
      details?.detail || "Registration failed.",
      response.status,
      details
    );
  }

  return response.json();
}

/**
 * Logs in an existing applicant account.
 * @param {string} email
 * @param {string} password
 * @returns {Promise<{ access_token: string, token_type: string }>}
 */
export async function login(email, password) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
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
      // Response body wasn't JSON.
    }

    throw new ApiError(
      details?.detail || "Login failed.",
      response.status,
      details
    );
  }

  return response.json();
}

/**
 * Stores the JWT access token in browser storage.
 * @param {string} token
 */
export function saveAccessToken(token) {
  localStorage.setItem("access_token", token);
}

/**
 * Retrieves the stored JWT access token.
 * @returns {string | null}
 */
export function getAccessToken() {
  return localStorage.getItem("access_token");
}

/**
 * Removes the stored JWT access token.
 */
export function clearAccessToken() {
  localStorage.removeItem("access_token");
}

/**
 * Builds the Authorization header for an authenticated request, using the
 * token already stored via saveAccessToken(). Returns an empty object if
 * there is no token, so callers can spread it into headers unconditionally.
 * @returns {{ Authorization?: string }}
 */
function authHeaders() {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
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
      headers: { "Content-Type": "application/json", ...authHeaders() },
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

    if (response.status === 401) {
      throw new ApiError(
        "Your session has expired. Please log in again.",
        response.status,
        details
      );
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
    response = await fetch(`${API_BASE_URL}/applications/${applicationId}`, {
      headers: { ...authHeaders() },
    });
  } catch (networkError) {
    throw new ApiError(
      "Could not reach the server. Check that the backend is running and try again.",
      null,
      networkError
    );
  }

  if (response.status === 401) {
    throw new ApiError("Your session has expired. Please log in again.", 401);
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

/**
 * Fetches all applications belonging to the authenticated user, newest first.
 * @returns {Promise<Array<object>>}
 */
export async function listApplications() {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/applications`, {
      headers: { ...authHeaders() },
    });
  } catch (networkError) {
    throw new ApiError(
      "Could not reach the server. Check that the backend is running and try again.",
      null,
      networkError
    );
  }

  if (response.status === 401) {
    throw new ApiError("Your session has expired. Please log in again.", 401);
  }

  if (!response.ok) {
    throw new ApiError(
      "Something went wrong on the server while loading your applications.",
      response.status
    );
  }

  return response.json();
}
