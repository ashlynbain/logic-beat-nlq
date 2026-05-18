import json
import os
import re
from typing import Optional

from .genre_profiles import get_profile
from .genres import detect_genre
from .models import BeatSpec

INSTRUMENT_ALIASES = {
    "kick": ["kick", "bd", "bass drum", "808 kick"],
    "snare": ["snare", "clap", "rim"],
    "hihat": ["hihat", "hi-hat", "hi hat", "hats", "hat"],
    "bass": ["bass", "sub", "808", "low end"],
    "synth": ["synth", "keys", "pad", "chord", "chords", "keyboard", "piano"],
    "perc": ["perc", "percussion", "shaker", "tamb"],
}


def _match_aliases(text: str, aliases: dict[str, list[str]]) -> list[str]:
    found: list[str] = []
    lower = text.lower()
    for canonical, terms in aliases.items():
        if any(term in lower for term in terms):
            found.append(canonical)
    return found


def parse_prompt_rule_based(prompt: str, bars: int = 8) -> BeatSpec:
    lower = prompt.lower()

    genre = detect_genre(prompt)

    profile = get_profile(genre)
    bpm = profile.default_bpm
    bpm_match = re.search(r"(\d{2,3})\s*bpm", lower)
    if bpm_match:
        bpm = max(60, min(200, int(bpm_match.group(1))))
    else:
        tempo_match = re.search(r"tempo\s*(?:of\s*)?(\d{2,3})", lower)
        if tempo_match:
            bpm = max(60, min(200, int(tempo_match.group(1))))

    instruments = _match_aliases(prompt, INSTRUMENT_ALIASES)
    if not instruments:
        instruments = list(profile.default_instruments)
    else:
        for core in ("kick", "hihat"):
            if core not in instruments and genre in ("rnb", "hiphop", "house"):
                pass
        if "snare" in instruments or "kick" in instruments:
            if "hihat" not in instruments:
                instruments.append("hihat")
    if genre == "hiphop":
        for essential in ("kick", "snare", "hihat"):
            if essential not in instruments:
                instruments.append(essential)

    key = "A"
    key_match = re.search(r"\b([a-g])(?:\s*(major|minor|maj|min))?\b", lower)
    if key_match:
        key = key_match.group(1).upper()

    scale = "minor"
    if any(w in lower for w in ("major", "maj", "happy", "bright")):
        scale = "major"
    if any(w in lower for w in ("minor", "min", "dark", "moody", "sad")):
        scale = "minor"

    mood = "smooth"
    if any(w in lower for w in ("aggressive", "hard", "energetic", "upbeat")):
        mood = "energetic"
    if any(w in lower for w in ("chill", "laid back", "laid-back", "slow")):
        mood = "chill"

    bars_match = re.search(r"(\d+)\s*bar", lower)
    if bars_match:
        bars = max(4, min(32, int(bars_match.group(1))))

    return BeatSpec(
        genre=genre,
        bpm=bpm,
        key=key,
        scale=scale,
        instruments=instruments,
        bars=bars,
        mood=mood,
    )


def parse_prompt_with_llm(prompt: str, bars: int = 8) -> Optional[BeatSpec]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            temperature=0.2,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract beat parameters from the user prompt. "
                        "Return JSON with keys: genre (rnb|hiphop|pop|house|lofi), bpm (int), "
                        "key (single letter A-G), scale (major|minor), instruments (array of: "
                        "kick, snare, hihat, bass, synth, perc), bars (int 4-32), mood (smooth|energetic|chill)."
                    ),
                },
                {"role": "user", "content": f"Prompt: {prompt}\nDefault bars if unspecified: {bars}"},
            ],
        )
        data = json.loads(response.choices[0].message.content or "{}")
        return BeatSpec(
            genre=data.get("genre", "rnb"),
            bpm=int(data.get("bpm", 120)),
            key=str(data.get("key", "A")).upper()[:1],
            scale=data.get("scale", "minor"),
            instruments=data.get("instruments") or ["kick", "snare", "hihat", "bass", "synth"],
            bars=int(data.get("bars", bars)),
            mood=data.get("mood", "smooth"),
        )
    except Exception:
        return None


def parse_prompt(prompt: str, bars: int = 8) -> BeatSpec:
    llm_spec = parse_prompt_with_llm(prompt, bars)
    if llm_spec:
        return llm_spec
    from .prompt_normalize import normalize_prompt

    spec, _ = normalize_prompt(prompt, bars)
    return spec
