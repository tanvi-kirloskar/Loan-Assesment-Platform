// Local | const API_BASE_URL = "http://127.0.0.1:8000";
const API_BASE_URL = "/api";
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
  const formData = new FormData();

  formData.append("full_name", payload.full_name);
  formData.append("monthly_income", String(payload.monthly_income));
  formData.append("loan_amount", String(payload.loan_amount));
  formData.append("loan_tenure_months", String(payload.loan_tenure_months));
  formData.append("loan_purpose", payload.loan_purpose);
  formData.append("existing_monthly_emi", String(payload.existing_monthly_emi));
  formData.append("credit_score", String(payload.credit_score));
  formData.append("credit_score_source", payload.credit_score_source || "MOCK");
  formData.append("payslip", payload.documents.PAYSLIP);
  formData.append("bank_statement", payload.documents.BANK_STATEMENT);
  formData.append("tax_return", payload.documents.TAX_RETURN);

  let response;

  try {
    response = await fetch(`${API_BASE_URL}/applications`, {
      method: "POST",
      headers: { ...authHeaders() },
      body: formData,
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
      // response body wasn't JSON.
    }

    if (response.status === 401) {
      throw new ApiError(
        "Your session has expired. Please log in again.",
        response.status,
        details
      );
    }

    if (response.status === 409) {
      throw new ApiError(
        details?.detail ||
          "One of the documents has already been uploaded.",
        response.status,
        details
      );
    }

    if (response.status === 422) {
      throw new ApiError(
        "The application couldn't be validated. Please check the required fields and documents.",
        response.status,
        details
      );
    }

    if (response.status === 400) {
      throw new ApiError(
        details?.detail ||
          "The application could not be submitted. Please check your details and documents.",
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

export async function resubmitApplication(applicationId) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/applications/${applicationId}/resubmit`,
      {
        method: "POST",
        headers: { ...authHeaders() },
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
    throw new ApiError("Your session has expired. Please log in again.", 401);
  }

  if (!response.ok) {
    let details = null;
    try {
      details = await response.json();
    } catch {
      // Response body wasn't JSON.
    }

    throw new ApiError(
      details?.detail || "The application could not be resubmitted.",
      response.status,
      details
    );
  }

  return response.json();
}

/**
 * Fetches the documents attached to a specific application.
 * @param {number} applicationId
 * @returns {Promise<Array<object>>}
 */
export async function viewDocument(applicationId, documentId) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/applications/${applicationId}/documents/${documentId}/view`,
      { headers: { ...authHeaders() } }
    );
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
    let details = null;
    try { details = await response.json(); } catch {}
    throw new ApiError(
      details?.detail || "The submitted document could not be found.",
      404,
      details
    );
  }

  if (!response.ok) {
    throw new ApiError(
      "The submitted document could not be opened.",
      response.status
    );
  }

  return response.blob();
}

export async function listDocuments(applicationId) {
  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/applications/${applicationId}/documents`,
      { headers: { ...authHeaders() } }
    );
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
    throw new ApiError("Application not found.", 404);
  }

  if (!response.ok) {
    throw new ApiError(
      "Something went wrong on the server while loading documents.",
      response.status
    );
  }

  return response.json();
}

/**
 * Uploads a supporting document for a specific application.
 * Uses FormData and intentionally does NOT set Content-Type manually —
 * the browser must generate the multipart boundary itself.
 * @param {number} applicationId
 * @param {string} documentType - e.g. "PAYSLIP" | "BANK_STATEMENT" | "TAX_RETURN"
 * @param {File} file
 * @returns {Promise<object>}
 */
export async function uploadDocument(applicationId, documentType, file) {
  const formData = new FormData();
  formData.append("document_type", documentType);
  formData.append("file", file);

  let response;

  try {
    response = await fetch(
      `${API_BASE_URL}/applications/${applicationId}/documents`,
      {
        method: "POST",
        headers: { ...authHeaders() },
        body: formData,
      }
    );
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
      // response body wasn't JSON
    }

    if (response.status === 401) {
      throw new ApiError(
        "Your session has expired. Please log in again.",
        401,
        details
      );
    }

    if (response.status === 409) {
      throw new ApiError(
        details?.detail ||
          "This document has already been uploaded. Please choose a different file.",
        409,
        details
      );
    }

    if (response.status === 422) {
      throw new ApiError(
        details?.detail ||
          "That file couldn't be uploaded. Check the file type and size.",
        422,
        details
      );
    }

    throw new ApiError(
      "Something went wrong on the server while uploading the document.",
      response.status,
      details
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


/** Returns the role claim from the stored JWT without requiring a backend call. */
export function getUserRole() {
  const token = getAccessToken();
  if (!token) return null;
  try {
    const payload = JSON.parse(
      decodeURIComponent(
        atob(token.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))
          .split("")
          .map((char) => "%" + ("00" + char.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      )
    );
    return payload.role || null;
  } catch {
    return null;
  }
}

async function advisorRequest(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...authHeaders(),
        ...(options.headers || {}),
      },
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
    let details = null;
    try { details = await response.json(); } catch {}
    const message =
      typeof details?.detail === "string"
        ? details.detail
        : Array.isArray(details?.detail)
          ? details.detail.map((e) => e.msg || JSON.stringify(e)).join("; ")
          : "The advisor request failed.";
    throw new ApiError(
      message,
      response.status,
      details
    );
  }

  return response.json();
}

export function listAdvisorApplications() {
  return advisorRequest("/advisor/applications");
}

export function getAdvisorApplication(applicationId) {
  return advisorRequest(`/advisor/applications/${applicationId}`);
}

export function getAdvisorWorkflow(applicationId) {
  return advisorRequest(`/advisor/applications/${applicationId}/workflow`);
}

export async function viewAdvisorDocument(applicationId, documentId) {
  let response;
  try {
    response = await fetch(
      `${API_BASE_URL}/advisor/applications/${applicationId}/documents/${documentId}/view`,
      { headers: { ...authHeaders() } }
    );
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
    let details = null;
    try { details = await response.json(); } catch {}
    throw new ApiError(
      details?.detail || "The submitted document could not be found.",
      404,
      details
    );
  }

  if (!response.ok) {
    throw new ApiError(
      "The submitted document could not be opened.",
      response.status
    );
  }

  return response.blob();
}


export function getAdvisorAudit(applicationId) {
  return advisorRequest(`/advisor/applications/${applicationId}/audit`);
}

export function submitAdvisorDecision(applicationId, action, notes) {
  return advisorRequest(`/advisor/applications/${applicationId}/decision`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, notes }),
  });
}

export function requestAdvisorInfo(applicationId, notes) {
  return advisorRequest(`/advisor/applications/${applicationId}/request-info`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action: "REQUEST_INFO", notes }),
  });
}
