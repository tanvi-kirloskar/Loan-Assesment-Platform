export const currencyFormatter = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 2,
});

// interest_rate arrives as a fraction, e.g. 0.09 -> "9.00%"
export function formatPercentFromFraction(value) {
  return `${(value * 100).toFixed(2)}%`;
}

// foir arrives already scaled as a percentage number, e.g. 25.47 -> "25.47%"
export function formatPercentValue(value) {
  return `${value.toFixed(2)}%`;
}

export function formatMultiplier(value) {
  return `${value.toFixed(2)}×`;
}

export function hasValue(value) {
  return value !== null && value !== undefined;
}

/**
 * Normalizes assessment_reasons into a clean array of individual reasons.
 * The backend currently stores this as a semicolon-delimited string, but
 * this also defensively handles an array shape in case that ever changes.
 * @param {string | string[] | null | undefined} reasons
 * @returns {string[]}
 */
export function getAssessmentReasons(reasons) {
  if (Array.isArray(reasons)) {
    return reasons.map((r) => r.trim()).filter(Boolean);
  }

  if (typeof reasons === "string") {
    return reasons
      .split(";")
      .map((r) => r.trim())
      .filter(Boolean);
  }

  return [];
}

/**
 * Summarizes an already-loaded list of applications for the dashboard
 * overview. This only counts existing decision values — it does not
 * calculate or infer anything the backend hasn't already provided.
 * @param {Array<object>} applications
 */
export function summarizeApplications(applications) {
  const total = applications.length;
  let approved = 0;
  let rejected = 0;

  for (const application of applications) {
    const decision = (application.decision || "").toUpperCase();
    if (decision === "APPROVED") approved += 1;
    if (decision === "REJECTED") rejected += 1;
  }

  // Backend returns applications newest first, so the first entry is latest.
  const latest = applications.length > 0 ? applications[0] : null;

  return { total, approved, rejected, latest };
}
