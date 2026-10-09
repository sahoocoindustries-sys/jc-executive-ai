from types import SimpleNamespace

import pytest

from jc.core.ai_provider import generate_response


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_gemini_provider_returns_text_and_usage(monkeypatch):
    calls = []
    monkeypatch.setattr(
        "jc.core.ai_provider.requests.post",
        lambda url, **kwargs: (
            calls.append((url, kwargs))
            or FakeResponse(
                {
                    "candidates": [
                        {"content": {"parts": [{"text": "Hello from JC"}]}}
                    ],
                    "usageMetadata": {
                        "promptTokenCount": 3,
                        "candidatesTokenCount": 4,
                    },
                }
            )
        ),
    )
    config = SimpleNamespace(
        GEMINI_API_KEY="test-gemini-key",
        OPENAI_API_KEY=None,
        OLLAMA_BASE_URL="http://localhost:11434",
    )

    text, tokens = generate_response(
        "Hello", "gemini-2.5-flash", 0.2, 100, config=config
    )

    assert text == "Hello from JC"
    assert tokens == 7
    assert "gemini-2.5-flash:generateContent" in calls[0][0]
    assert calls[0][1]["headers"]["x-goog-api-key"] == "test-gemini-key"


def test_openai_provider_returns_text_and_usage(monkeypatch):
    monkeypatch.setattr(
        "jc.core.ai_provider.requests.post",
        lambda url, **kwargs: FakeResponse(
            {
                "choices": [{"message": {"content": "Hello from OpenAI"}}],
                "usage": {"total_tokens": 9},
            }
        ),
    )
    config = SimpleNamespace(
        GEMINI_API_KEY=None,
        OPENAI_API_KEY="test-openai-key",
        OLLAMA_BASE_URL="http://localhost:11434",
    )

    text, tokens = generate_response("Hello", "gpt-4o-mini", 0.4, 120, config=config)

    assert text == "Hello from OpenAI"
    assert tokens == 9


def test_missing_provider_key_fails_instead_of_faking_a_response():
    config = SimpleNamespace(
        GEMINI_API_KEY=None,
        OPENAI_API_KEY=None,
        OLLAMA_BASE_URL="http://localhost:11434",
    )

    with pytest.raises(RuntimeError, match="API key is not configured"):
        generate_response("Hello", "gpt-4o-mini", 0.4, 120, config=config)
