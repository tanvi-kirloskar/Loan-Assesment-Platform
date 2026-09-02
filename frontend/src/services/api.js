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
 * Returns the JWT access token stored in the browser.
 */
export function getAccessToken() {
  return localStorage.getItem("access_token");
}

/**
 * Saves the JWT access token in the browser.
 */
export function saveAccessToken(accessToken) {
  localStorage.setItem("access_token", accessToken);
}

/**
 * Removes the JWT access token from the browser.
 */
export function clearAccessToken() {
  localStorage.removeItem("access_token");
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
      headers: {
        "Content-Type": "application/json",
      },
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
      headers: {
        "Content-Type": "application/json",
      },
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
 * Submits a new loan application.
 */
export async function createApplication(payload) {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new ApiError(
      "You are not logged in. Please log in and try again.",
      401
    );
  }

  let response;

  try {
    response = await fetch(`${API_BASE_URL}/applications`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
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
      // Response body wasn't JSON.
    }

    if (response.status === 401) {
      throw new ApiError(
        "Your login session is invalid or has expired. Please log in again.",
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
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new ApiError(
      "You are not logged in. Please log in and try again.",
      401
    );
  }

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/applications/${applicationId}`,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      }
    );
  } catch (networkError) {
    throw new ApiError(
      "Could not reach the server. Check that the backend is running and try again.",
      null,
      networkError
    );
  }

  if (response.status === 401) {
    throw new ApiError(
      "Your login session is invalid or has expired. Please log in again.",
      response.status
    );
  }

  if (response.status === 404) {
    throw new ApiError(
      "No application found with that ID.",
      404
    );
  }

  if (!response.ok) {
    throw new ApiError(
      "Something went wrong on the server while fetching the application.",
      response.status
    );
  }

  return response.json();
}