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
