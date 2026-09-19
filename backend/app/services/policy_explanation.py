import os

from dotenv import load_dotenv
from google import genai


load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


def create_gemini_client() -> genai.Client:
    """Create a Gemini client using the backend environment."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is not set."
        )

    return genai.Client(api_key=api_key)


def generate_policy_explanation(
    evidence: list[dict],
    findings: list[dict],
    policy_chunks: list[dict],
    assessment_result: dict | None = None,
) -> str:
    """Generate a grounded explanation using retrieved policy."""

    client = create_gemini_client()

    policy_text = "\n\n".join(
        f"Policy Section: {chunk['section']}\n"
        f"{chunk['content']}"
        for chunk in policy_chunks
    )

    prompt = f"""
You are an AI assistant supporting a loan assessment workflow.

Explain the supplied verification results using ONLY the supplied
evidence, findings, assessment result, and policy context.

Rules:
- Do not invent policy rules.
- Do not approve or reject the loan.
- Do not override the deterministic financial assessment.
- Do not invent facts.
- Clearly distinguish evidence, findings, and policy guidance.
- If the policy does not answer something, say so.
- Keep the explanation concise and factual.

EVIDENCE:
{evidence}

VERIFICATION FINDINGS:
{findings}

DETERMINISTIC ASSESSMENT RESULT:
{assessment_result}

RETRIEVED POLICY:
{policy_text}

Provide:
1. A short explanation of the relevant findings.
2. The policy basis for those findings.
3. Any workflow action supported by the findings and policy.
"""

    interaction = client.interactions.create(
        model=MODEL_NAME,
        input=prompt,
    )

    return interaction.output_text