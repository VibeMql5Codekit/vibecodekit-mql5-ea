"""Optional LLM provider adapters for Prompt Architect."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

from vibecodekit_mql5.prompt_architect.render import (
    render_blueprint,
    render_prompt,
    render_requirements,
)

LLM_PROVIDERS = ("prompt-only", "openai", "gemini")
PROVIDER_ENV = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
DEFAULT_MODELS = {
    "prompt-only": "manual-codegen-review",
    "openai": "gpt-4o-mini",
    "gemini": "gemini-1.5-flash",
}


def render_codegen_prompt(config: dict[str, object]) -> str:
    """Render a provider-neutral codegen prompt without calling an LLM."""
    return f"""# Optional LLM codegen prompt: {config['name']}

Generated code is only a draft. It is not accepted until the vibecodekit gates pass.

## Implementation prompt

{render_prompt(config).strip()}

## Requirements traceability

```json
{render_requirements(config)}
```

## Blueprint

{render_blueprint(config).strip()}

## Provider rules

1. Do not invent broker constraints, API keys, Telegram tokens, license secrets, or account IDs.
2. Use existing scaffold structure and vibecodekit libraries.
3. Do not remove risk, spread, stop-loss, drawdown, or max-position guards.
4. Return code changes only; tests/gates must run separately.
5. If requirements conflict, stop and report the conflict instead of guessing.
"""


def _redact_known_secrets(text: str) -> str:
    safe = text
    for env_name in PROVIDER_ENV.values():
        value = os.environ.get(env_name, "")
        if len(value) >= 8:
            safe = safe.replace(value, "[REDACTED]")
    return safe


def _env_secret_leaks(text: str) -> list[str]:
    leaks = []
    for env_name in PROVIDER_ENV.values():
        value = os.environ.get(env_name, "")
        if len(value) >= 8 and value in text:
            leaks.append(env_name)
    return leaks


def _safe_error(exc: BaseException) -> str:
    return _redact_known_secrets(str(exc))


def _openai_codegen(prompt: str, model: str, endpoint: str | None, timeout: int) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("missing required environment variable: OPENAI_API_KEY")
    url = endpoint or "https://api.openai.com/v1/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a careful MQL5 implementation assistant.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }
    ).encode()
    request = urllib.request.Request(
        url,
        body,
        {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read())
    return str(data["choices"][0]["message"]["content"])


def _gemini_codegen(prompt: str, model: str, endpoint: str | None, timeout: int) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("missing required environment variable: GEMINI_API_KEY")
    url = endpoint or (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    )
    body = json.dumps(
        {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}],
                }
            ],
            "generationConfig": {"temperature": 0.1},
        }
    ).encode()
    request = urllib.request.Request(url, body, {"Content-Type": "application/json",
                                                "x-goog-api-key": api_key})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read())
    parts = data["candidates"][0]["content"]["parts"]
    return "\n".join(str(part.get("text", "")) for part in parts).strip()


def run_llm_codegen(
    config: dict[str, object],
    provider: str,
    model: str | None = None,
    endpoint: str | None = None,
    timeout: int = 30,
) -> dict[str, object]:
    """Prepare or execute optional provider-backed codegen."""
    if provider not in LLM_PROVIDERS:
        return {"provider": provider, "status": "invalid-provider",
                "error": f"provider must be one of {list(LLM_PROVIDERS)}"}

    selected_model = model or DEFAULT_MODELS[provider]
    prompt = render_codegen_prompt(config)
    leaks = _env_secret_leaks(prompt)
    if leaks:
        return {
            "provider": provider,
            "model": selected_model,
            "status": "blocked-secret-leak",
            "error": f"prompt contains environment secret values: {', '.join(leaks)}",
        }

    if provider == "prompt-only":
        return {
            "provider": provider,
            "model": selected_model,
            "status": "prompt-ready",
            "content": prompt,
        }

    try:
        if provider == "openai":
            content = _openai_codegen(prompt, selected_model, endpoint, timeout)
        else:
            content = _gemini_codegen(prompt, selected_model, endpoint, timeout)
    except (RuntimeError, OSError, ValueError, urllib.error.URLError, KeyError, IndexError) as exc:
        return {
            "provider": provider,
            "model": selected_model,
            "status": "error",
            "error": _safe_error(exc),
        }

    return {"provider": provider, "model": selected_model, "status": "ok", "content": content}
