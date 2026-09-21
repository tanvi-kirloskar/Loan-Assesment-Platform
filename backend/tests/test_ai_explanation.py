from app.services.ai_explanation import (
    build_explanation_prompt,
    deterministic_fallback,
    generate_ai_explanation,
)


def test_fallback_preserves_deterministic_decision():
    assessment = {
        "decision": "REJECTED",
        "reasons": ["FOIR exceeds configured threshold."],
    }

    result = deterministic_fallback(assessment, [])

    assert "REJECTED" in result
    assert "FOIR exceeds configured threshold." in result


def test_prompt_contains_policy_and_assessment_but_not_raw_document_content():
    assessment = {
        "decision": "APPROVED",
        "reasons": [],
        "foir": "40.00",
    }
    findings = [
        {
            "finding_type": "NAME_MATCH",
            "message": "Name matches.",
        }
    ]
    policy = [
        {
            "source": "loan_assessment_policy.md",
            "section": "FOIR",
            "content": "The configured maximum FOIR is 50%.",
        }
    ]

    prompt = build_explanation_prompt(assessment, findings, policy)

    assert "APPROVED" in prompt
    assert "FOIR" in prompt
    assert "50%" in prompt
    assert "raw document" not in prompt.lower()


def test_gemini_response_is_parsed_without_changing_decision(monkeypatch):
    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {"text": "The application is explained using the supplied policy."}
                            ]
                        }
                    }
                ]
            }

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("app.services.ai_explanation.httpx.post", fake_post)

    result = generate_ai_explanation(
        assessment={"decision": "REJECTED", "reasons": ["FOIR exceeds threshold."]},
        findings=[],
        policy_context=[
            {
                "source": "loan_assessment_policy.md",
                "section": "FOIR",
                "content": "Maximum FOIR is 50%.",
            }
        ],
        api_key="test-key",
    )

    assert result == "The application is explained using the supplied policy."


def test_gemini_503_falls_back_to_deterministic_explanation(monkeypatch):
    class FakeResponse:
        status_code = 503
        request = __import__("httpx").Request("POST", "https://example.test")

        def raise_for_status(self):
            raise __import__("httpx").HTTPStatusError(
                "503 Service Unavailable",
                request=__import__("httpx").Request("POST", "https://example.test"),
                response=self,
            )

    def fake_post(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("app.services.ai_explanation.httpx.post", fake_post)
    monkeypatch.setattr("app.services.ai_explanation.time.sleep", lambda _: None)

    result = generate_ai_explanation(
        assessment={
            "decision": "REJECTED",
            "reasons": ["FOIR exceeds configured threshold."],
        },
        findings=[],
        policy_context=[],
        api_key="test-key",
    )

    assert "REJECTED" in result
    assert "FOIR exceeds configured threshold." in result
