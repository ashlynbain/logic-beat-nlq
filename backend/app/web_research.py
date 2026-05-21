"""Optional Tavily web search to enrich obscure or reference-heavy beat prompts."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

TAVILY_SEARCH_URL = "https://api.tavily.com/search"
_MAX_SNIPPET = 400


def fetch_beat_research(
    prompt: str,
    *,
    tavily_api_key: str | None = None,
) -> tuple[str | None, list[str]]:
    """
    Search for production context (BPM, genre, feel) for the user's prompt.

    Returns (context_text, adjustment_notes). context_text is None if skipped or failed.
    """
    api_key = (tavily_api_key or "").strip() or os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        return None, ["Web search skipped — add a Tavily API key in the quest settings."]

    query = (
        f"music production instrumental beat {prompt} "
        "BPM tempo genre drum pattern key signature mood"
    )

    try:
        payload = json.dumps(
            {
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": 5,
                "include_answer": True,
            }
        ).encode("utf-8")
        req = urllib.request.Request(
            TAVILY_SEARCH_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return None, [f"Web search failed (HTTP {exc.code}). Using your prompt only."]
    except Exception as exc:
        return None, [f"Web search unavailable ({exc}). Using your prompt only."]

    parts: list[str] = []
    answer = (data.get("answer") or "").strip()
    if answer:
        parts.append(answer)

    for hit in data.get("results") or []:
        content = (hit.get("content") or "").strip()
        if not content:
            continue
        title = (hit.get("title") or "source").strip()
        snippet = content[:_MAX_SNIPPET]
        if len(content) > _MAX_SNIPPET:
            snippet += "…"
        parts.append(f"{title}: {snippet}")

    if not parts:
        return None, ["Web search returned no useful snippets. Using your prompt only."]

    context = "\n".join(parts)
    notes = [
        "Tavily added production references to interpret your prompt.",
    ]
    return context, notes
