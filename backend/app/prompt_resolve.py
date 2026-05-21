"""Combine rule-based parsing, optional web context, and optional LLM extraction."""

from __future__ import annotations

import os
import zlib

from .client_keys import ClientApiKeys
from .llm_providers import parse_with_llm, resolve_llm_from_env
from .models import BeatSpec
from .prompt_normalize import normalize_prompt
from .web_research import fetch_beat_research


def resolve_beat_spec(
    prompt: str,
    bars: int,
    *,
    use_web_search: bool = False,
    client_keys: ClientApiKeys | None = None,
) -> tuple[BeatSpec, list[str], str | None]:
    """
    Build BeatSpec from prompt.

    Returns (spec, adjustments, web_context_or_none).
    """
    adjustments: list[str] = []
    web_context: str | None = None
    parse_input = prompt
    keys = client_keys or ClientApiKeys()

    if use_web_search:
        tavily_key = keys.tavily_api_key if keys.tavily_configured() else None
        web_context, web_notes = fetch_beat_research(prompt, tavily_api_key=tavily_key)
        adjustments.extend(web_notes)
        if web_context:
            parse_input = f"{prompt}\n\nProduction references:\n{web_context}"

    spec, norm_notes = normalize_prompt(parse_input, bars)
    adjustments.extend(norm_notes)

    llm_spec = None
    llm_label: str | None = None

    if keys.llm_configured() and keys.llm_provider and keys.llm_api_key:
        llm_spec, llm_label = parse_with_llm(
            keys.llm_provider,
            keys.llm_api_key.strip(),
            prompt,
            bars,
            web_context=web_context,
            model=keys.llm_model,
        )
        if llm_spec:
            adjustments.append(f"Refined parameters with {llm_label} (your key, not stored).")
        else:
            adjustments.append(f"{llm_label or 'LLM'} — using rule-based parameters.")
    else:
        llm_spec, llm_label = resolve_llm_from_env(prompt, bars, web_context)
        if llm_spec and llm_label:
            adjustments.append(f"Refined parameters with {llm_label} (server env).")

    if llm_spec:
        spec = llm_spec
        spec.bars = bars
    elif not keys.llm_configured() and not os.getenv("OPENAI_API_KEY"):
        if use_web_search and web_context:
            adjustments.append("Using rule-based parsing with web search context.")
        elif keys.llm_provider and not keys.llm_api_key:
            adjustments.append("Add an LLM API key in quest settings for smarter parsing.")

    if spec.variation == 0:
        spec.variation = zlib.adler32(prompt.strip().lower().encode()) & 0xFFFFFFFF

    spec.bars = bars
    return spec, adjustments, web_context
