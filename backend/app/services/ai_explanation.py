from __future__ import annotations

import json
import os
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
        f"- {item.get('finding_type')}: {item.get('message')}"
        for item in findings
    )

    return f"""Explain this loan assessment for an internal reviewer.

Deterministic D3 assessment:
Decision: {assessment.get("decision")}
Reasons: {json.dumps(assessment.get("reasons", []))}
FOIR: {assessment.get("foir")}
LTI: {assessment.get("lti")}
Interest rate: {assessment.get("interest_rate")}
EMI: {assessment.get("emi")}

Verification findings:
{finding_text or "- None"}

Retrieved policy evidence:
{policy_text or "- None"}

Rules:
1. Explain the deterministic D3 result; do not change, override, or invent a decision.
2. Use only the supplied policy evidence for policy claims.
3. Do not invent facts about the applicant or documents.
4. Keep the explanation concise and suitable for an internal reviewer.
5. Clearly distinguish verification findings from the financial assessment.
"""


def deterministic_fallback(
    assessment: dict[str, Any],
    policy_context: list[dict[str, Any]],
) -> str:
    decision = assessment.get("decision", "UNKNOWN")
    reasons = assessment.get("reasons") or []
    reason_text = " ".join(str(reason) for reason in reasons)

    if reason_text:
        return (
            f"D3 assessment decision: {decision}. "
            f"Deterministic reason(s): {reason_text}"
        )

    if policy_context:
        sections = ", ".join(item["section"] for item in policy_context[:3])
        return (
            f"D3 assessment decision: {decision}. "
            f"Relevant policy sections: {sections}."
        )

    return f"D3 assessment decision: {decision}."


def generate_ai_explanation(
    *,
    assessment: dict[str, Any],
    findings: list[dict[str, Any]],
    policy_context: list[dict[str, Any]],
    api_key: str | None = None,
    model: str | None = None,
    timeout: float = 20.0,
) -> str:
    """Generate a policy-grounded explanation, with a safe local fallback.

    The Gemini call is deliberately isolated from the deterministic D3
    assessment. Missing credentials never prevent the workflow from running.
    """
    api_key = api_key or os.getenv("GEMINI_API_KEY")
    model = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    if not api_key:
        return deterministic_fallback(assessment, policy_context)

    prompt = build_explanation_prompt(assessment, findings, policy_context)
    url = f"{GEMINI_API_URL}/{model}:generateContent"

    response = httpx.post(
        url,
        params={"key": api_key},
        json={
            "contents": [
                {
                    "parts": [{"text": prompt}],
                }
            ]
        },
        timeout=timeout,
    )
    response.raise_for_status()

    payload = response.json()
    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError("Gemini returned an unexpected response shape.") from exc
