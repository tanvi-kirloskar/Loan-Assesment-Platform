from __future__ import annotations

import json
import os
import time
from typing import Any

import httpx


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def build_explanation_prompt(
    assessment: dict[str, Any],
    findings: list[dict[str, Any]],
    policy_context: list[dict[str, Any]],
) -> str:
    policy_text = "\n\n".join(
        f"[{item['source']} — {item['section']}]\n{item['content']}"
        for item in policy_context
    )
    finding_text = "\n".join(
        f"- {item.get('finding_type')}: {item.get('message')} "
        f"(severity={item.get('severity')}, action={item.get('action')})"
        for item in findings
    )

    return f"""You are an AI explanation assistant for an internal loan advisor.

Explain an already-computed Rule-Based Loan Assessment. The Python assessment
engine is authoritative. Your job is only to turn the supplied facts and
retrieved policy evidence into a clear, professional advisor-facing explanation.

ASSESSMENT FACTS
Decision: {assessment.get("decision")}
Decision reasons: {json.dumps(assessment.get("reasons", []))}
Monthly income: {assessment.get("monthly_income")}
Existing monthly EMI: {assessment.get("existing_monthly_emi")}
Loan amount: {assessment.get("loan_amount")}
Loan tenure (months): {assessment.get("loan_tenure_months")}
Loan purpose: {assessment.get("loan_purpose")}
Proposed EMI: {assessment.get("emi")}
FOIR: {assessment.get("foir")}
LTI: {assessment.get("lti")}
Credit score: {assessment.get("credit_score")}
Interest rate: {assessment.get("interest_rate")}

CONFIGURED ASSESSMENT THRESHOLDS
Minimum credit score: {assessment.get("minimum_credit_score")}
Maximum FOIR: {assessment.get("maximum_foir")}%
Maximum LTI: {assessment.get("maximum_lti")}x

VERIFICATION FINDINGS
{finding_text or "- None"}

RETRIEVED POLICY EVIDENCE
{policy_text or "- None"}

Return ONLY valid JSON with exactly these string fields:
{{
  "summary": "A concise 2-4 sentence explanation of the assessment outcome.",
  "financial_factors": "Explain the financial parameters that materially support or trigger the outcome. Include the relevant actual values and configured thresholds.",
  "policy_basis": "Explain which supplied policy rules support the assessment. Do not invent or generalize policy beyond the supplied evidence.",
  "verification_context": "Explain whether verification findings affect the advisor's review. Clearly say when there are no findings.",
  "advisor_focus": "State what the advisor should pay attention to when reviewing the application. Do not make a new approval or rejection decision."
}}

Rules:
1. Never calculate or invent values that are not supplied.
2. Never change, override, or independently make the assessment decision.
3. Never invent applicant facts, document facts, policy rules, or verification findings.
4. Use the supplied policy evidence for policy claims.
5. Explain the supplied numbers in plain language suitable for a loan advisor.
6. Keep each field concise and useful.
7. Clearly distinguish the Rule-Based Loan Assessment from document verification and the later human advisor decision.
"""


def _fallback_text(
    assessment: dict[str, Any],
    findings: list[dict[str, Any]],
    policy_context: list[dict[str, Any]],
) -> dict[str, str]:
    decision = assessment.get("decision", "UNKNOWN")
    reasons = assessment.get("reasons") or []
    reason_text = " ".join(str(reason) for reason in reasons)

    financial_parts = []
    if assessment.get("credit_score") is not None:
        financial_parts.append(
            f"Credit score is {assessment['credit_score']} "
            f"against a configured minimum of {assessment.get('minimum_credit_score')}."
        )
    if assessment.get("foir") is not None:
        financial_parts.append(
            f"FOIR is {assessment['foir']}% against a configured maximum of "
            f"{assessment.get('maximum_foir')}%."
        )
    if assessment.get("lti") is not None:
        financial_parts.append(
            f"LTI is {assessment['lti']}x against a configured maximum of "
            f"{assessment.get('maximum_lti')}x."
        )

    summary = (
        f"The Rule-Based Loan Assessment resulted in {decision}."
        + (f" {reason_text}" if reason_text else " No assessment rejection conditions were triggered.")
    )

    policy_summary = (
        "The assessment is supported by the retrieved policy evidence: "
        + ", ".join(item["section"] for item in policy_context[:3]) + "."
        if policy_context
        else "No retrieved policy evidence was available for the explanation."
    )

    verification_summary = (
        "Verification findings require attention: "
        + " ".join(str(item.get("message")) for item in findings)
        if findings
        else "No verification findings were identified in the latest run."
    )

    advisor_focus = (
        "Review the supplied financial inputs, supporting evidence, and policy context "
        "before recording the human advisor decision."
    )

    return {
        "summary": summary,
        "financial_factors": " ".join(financial_parts) or "No financial metrics were supplied.",
        "policy_basis": policy_summary,
        "verification_context": verification_summary,
        "advisor_focus": advisor_focus,
    }


def deterministic_fallback(
    assessment: dict[str, Any],
    policy_context: list[dict[str, Any]],
    findings: list[dict[str, Any]] | None = None,
) -> dict[str, str]:
    """Return a grounded explanation when Gemini is unavailable."""
    return _fallback_text(assessment, findings or [], policy_context)


def _parse_gemini_explanation(payload: dict[str, Any]) -> dict[str, str]:
    text = payload["candidates"][0]["content"]["parts"][0]["text"].strip()
    fence = chr(96) * 3
    if text.startswith(fence):
        text = text.replace(fence + "json", "", 1).replace(fence, "", 1).strip()

    parsed = json.loads(text)
    required = (
        "summary",
        "financial_factors",
        "policy_basis",
        "verification_context",
        "advisor_focus",
    )

    if not isinstance(parsed, dict) or any(
        not isinstance(parsed.get(key), str) or not parsed[key].strip()
        for key in required
    ):
        raise ValueError("Gemini returned an incomplete explanation.")

    return {key: parsed[key].strip() for key in required}


def generate_ai_explanation(
    *,
    assessment: dict[str, Any],
    findings: list[dict[str, Any]],
    policy_context: list[dict[str, Any]],
    api_key: str | None = None,
    model: str | None = None,
    timeout: float = 20.0,
) -> dict[str, str]:
    """Generate a policy-grounded advisor explanation with a safe local fallback.

    Gemini only explains supplied facts. It never owns the assessment decision.
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    model = model or os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    if not api_key:
        return deterministic_fallback(assessment, policy_context, findings)

    prompt = build_explanation_prompt(assessment, findings, policy_context)
    url = f"{GEMINI_API_URL}/{model}:generateContent"

    request_body = {
        "contents": [
            {
                "parts": [{"text": prompt}],
            }
        ]
    }

    last_error: Exception | None = None

    for attempt in range(3):
        try:
            response = httpx.post(
                url,
                headers={"x-goog-api-key": api_key},
                json=request_body,
                timeout=timeout,
            )

            if response.status_code >= 500:
                last_error = httpx.HTTPStatusError(
                    f"Gemini service returned {response.status_code}.",
                    request=response.request,
                    response=response,
                )
                if attempt < 2:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                return deterministic_fallback(assessment, policy_context, findings)

            response.raise_for_status()
            return _parse_gemini_explanation(response.json())

        except (httpx.HTTPError, KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < 2:
                time.sleep(1.0 * (attempt + 1))
                continue
            return deterministic_fallback(assessment, policy_context, findings)

    if last_error is not None:
        return deterministic_fallback(assessment, policy_context, findings)
    return deterministic_fallback(assessment, policy_context, findings)
