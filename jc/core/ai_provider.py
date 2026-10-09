"""Small, explicit provider adapter for real model inference.

The adapter never fabricates a response: missing credentials and provider errors
are surfaced to the API layer for safe error handling.
"""
from typing import Any

import requests


def generate_response(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    *,
    config: Any,
) -> tuple[str, int]:
    """Call a configured Gemini, OpenAI-compatible, or Ollama model."""
    if model.startswith(("gemini-", "models/gemini-")):
        api_key = getattr(config, "GEMINI_API_KEY", None)
        if not api_key:
            raise RuntimeError("Gemini API key is not configured")
        model_name = model.removeprefix("models/")
        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent",
            headers={"x-goog-api-key": api_key},
            json={
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        candidates = payload.get("candidates") or []
        if not candidates:
            raise RuntimeError("Gemini returned no response candidates")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(part.get("text", "") for part in parts).strip()
        if not text:
            raise RuntimeError("Gemini returned an empty response")
        usage = payload.get("usageMetadata", {})
        tokens = int(usage.get("promptTokenCount", 0)) + int(
            usage.get("candidatesTokenCount", 0)
        )
        return text, tokens

    if model.startswith(("gpt-", "o1", "o3", "o4")):
        api_key = getattr(config, "OPENAI_API_KEY", None)
        if not api_key:
            raise RuntimeError("OpenAI API key is not configured")
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
            timeout=60,
        )
        response.raise_for_status()
        payload = response.json()
        choices = payload.get("choices") or []
        if not choices:
            raise RuntimeError("OpenAI returned no response choices")
        text = (choices[0].get("message", {}).get("content") or "").strip()
        if not text:
            raise RuntimeError("OpenAI returned an empty response")
        return text, int(payload.get("usage", {}).get("total_tokens", 0))

    if model.startswith("ollama:"):
        model_name = model.split(":", 1)[1].strip()
        if not model_name:
            raise ValueError("Ollama model name is required after 'ollama:'")
        base_url = getattr(config, "OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        response = requests.post(
            f"{base_url}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            },
            timeout=120,
        )
        response.raise_for_status()
        payload = response.json()
        text = (payload.get("response") or "").strip()
        if not text:
            raise RuntimeError("Ollama returned an empty response")
        tokens = int(payload.get("prompt_eval_count", 0)) + int(
            payload.get("eval_count", 0)
        )
        return text, tokens

    raise ValueError(
        "Unsupported model. Use a Gemini model, an OpenAI model, or ollama:<model-name>."
    )
