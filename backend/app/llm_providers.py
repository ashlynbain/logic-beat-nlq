"""Parse beat prompts with user-supplied LLM API keys (never persisted)."""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Literal, Optional

from .models import BeatSpec

LlmProvider = Literal["openai", "anthropic", "google"]

_SYSTEM = (
    "Extract beat parameters from the user prompt. "
    "Return ONLY valid JSON with keys: genre (rnb|hiphop|pop|house|lofi), bpm (int), "
    "key (single letter A-G), scale (major|minor), instruments (array of: "
    "kick, snare, hihat, bass, synth, perc), bars (int 4-32), mood (smooth|energetic|chill)."
)

_DEFAULT_MODELS: dict[LlmProvider, str] = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-3-5-haiku-20241022",
    "google": "gemini-1.5-flash",
}


def _user_message(prompt: str, bars: int, web_context: str | None) -> str:
    text = f"Prompt: {prompt}\nDefault bars if unspecified: {bars}"
    if web_context:
        text += f"\n\nWeb research (use for BPM/genre/mood when the prompt is vague):\n{web_context}"
    return text


def _spec_from_json(data: dict, bars: int) -> BeatSpec:
    return BeatSpec(
        genre=data.get("genre", "rnb"),
        bpm=int(data.get("bpm", 120)),
        key=str(data.get("key", "A")).upper()[:1],
        scale=data.get("scale", "minor"),
        instruments=data.get("instruments") or ["kick", "snare", "hihat", "bass", "synth"],
        bars=int(data.get("bars", bars)),
        mood=data.get("mood", "smooth"),
    )


def _extract_json(text: str) -> dict:
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            return json.loads(match.group(0))
        raise


def parse_with_openai(
    api_key: str,
    model: str,
    prompt: str,
    bars: int,
    web_context: str | None,
) -> BeatSpec:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": _user_message(prompt, bars, web_context)},
        ],
    )
    data = _extract_json(response.choices[0].message.content or "{}")
    return _spec_from_json(data, bars)


def parse_with_anthropic(
    api_key: str,
    model: str,
    prompt: str,
    bars: int,
    web_context: str | None,
) -> BeatSpec:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        temperature=0.2,
        system=_SYSTEM + " Respond with JSON only, no markdown.",
        messages=[{"role": "user", "content": _user_message(prompt, bars, web_context)}],
    )
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text
    data = _extract_json(text)
    return _spec_from_json(data, bars)


def parse_with_google(
    api_key: str,
    model: str,
    prompt: str,
    bars: int,
    web_context: str | None,
) -> BeatSpec:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    body = {
        "contents": [
            {
                "parts": [
                    {"text": _SYSTEM + "\n\n" + _user_message(prompt, bars, web_context)},
                ],
            }
        ],
        "generationConfig": {"temperature": 0.2, "responseMimeType": "application/json"},
    }
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    candidates = data.get("candidates") or []
    if not candidates:
        raise ValueError("No response from Gemini")
    parts = candidates[0].get("content", {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts)
    return _spec_from_json(_extract_json(text), bars)


def parse_with_llm(
    provider: LlmProvider,
    api_key: str,
    prompt: str,
    bars: int,
    web_context: str | None = None,
    model: str | None = None,
) -> tuple[Optional[BeatSpec], str]:
    """
    Use a one-off API key from the client. Returns (spec, label) or (None, error_hint).
    """
    model = (model or "").strip() or _DEFAULT_MODELS[provider]
    try:
        if provider == "openai":
            spec = parse_with_openai(api_key, model, prompt, bars, web_context)
            return spec, f"OpenAI ({model})"
        if provider == "anthropic":
            spec = parse_with_anthropic(api_key, model, prompt, bars, web_context)
            return spec, f"Anthropic ({model})"
        if provider == "google":
            spec = parse_with_google(api_key, model, prompt, bars, web_context)
            return spec, f"Google ({model})"
    except urllib.error.HTTPError as exc:
        return None, f"{provider} API error (HTTP {exc.code})"
    except Exception as exc:
        return None, f"{provider} parse failed ({exc})"
    return None, "Unknown provider"


def resolve_llm_from_env(
    prompt: str,
    bars: int,
    web_context: str | None,
) -> tuple[Optional[BeatSpec], str | None]:
    """Fallback: server .env OpenAI key only (legacy)."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None, None
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    spec, label = parse_with_llm("openai", api_key, prompt, bars, web_context, model)
    return spec, label
