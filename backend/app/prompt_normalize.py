"""Rewrite vague or mismatched prompts into production-ready beat specs."""

from __future__ import annotations

import re
import zlib

from .genre_profiles import get_profile
from .genres import detect_genre
from .models import BeatSpec

INSTRUMENT_ALIASES = {
    "kick": ["kick", "bd", "bass drum"],
    "snare": ["snare", "clap", "rim"],
    "hihat": ["hihat", "hi-hat", "hi hat", "hats", "hat"],
    "bass": ["bass", "sub", "808", "low end"],
    "synth": ["synth", "keys", "pad", "chord", "chords", "keyboard", "piano", "rhodes"],
    "perc": ["perc", "percussion", "shaker", "tamb"],
}


def _match(text: str, aliases: dict[str, list[str]]) -> list[str]:
    lower = text.lower()
    found = []
    for name, terms in aliases.items():
        if any(t in lower for t in terms):
            found.append(name)
    return found


def normalize_prompt(prompt: str, bars: int = 8) -> tuple[BeatSpec, list[str]]:
    notes: list[str] = []
    lower = prompt.lower()

    genre = detect_genre(prompt)
    profile = get_profile(genre)

    if genre == "lofi":
        notes.append(f"Detected lo-fi / chillhop ({profile.name}) — not R&B.")

    bpm = profile.default_bpm
    bpm_match = re.search(r"(\d{2,3})\s*bpm", lower)
    if bpm_match:
        bpm = int(bpm_match.group(1))
    else:
        tempo_match = re.search(r"tempo\s*(?:of\s*)?(\d{2,3})", lower)
        if tempo_match:
            bpm = int(tempo_match.group(1))

    lo, hi = profile.bpm_range
    user_set_bpm = bool(bpm_match or tempo_match)
    if not user_set_bpm:
        if bpm < lo or bpm > hi:
            bpm = profile.default_bpm
            notes.append(f"Using {bpm} BPM (default for {profile.name}).")
    elif bpm < 60 or bpm > 200:
        bpm = max(60, min(200, bpm))
        notes.append(f"Tempo limited to {bpm} BPM.")

    key = "D" if genre == "lofi" else "A"
    key_match = re.search(r"\b([a-g])(?:\s*(major|minor|maj|min))?\b", lower)
    if key_match:
        key = key_match.group(1).upper()

    scale = "minor"
    if any(w in lower for w in ("major", "maj", "happy", "bright", "uplifting")):
        scale = "major"
    if any(w in lower for w in ("minor", "min", "dark", "moody", "sad", "smooth", "chill")):
        scale = "minor"
    if genre == "rnb" and scale == "major" and "major" not in lower and "maj" not in lower:
        notes.append("Set key to minor — most vocal R&B beds are minor or modal.")
        scale = "minor"

    mood = "smooth"
    if genre == "lofi":
        mood = "chill"
    if any(w in lower for w in ("aggressive", "hard", "energetic", "upbeat", "party")):
        mood = "energetic"
    if any(w in lower for w in ("chill", "laid back", "laid-back", "slow", "bed", "sleep", "study")):
        mood = "chill"

    instruments = _match(prompt, INSTRUMENT_ALIASES)
    if not instruments:
        instruments = list(profile.default_instruments)
        notes.append(f"Using {profile.name} stack: {', '.join(instruments)}.")
    else:
        if genre in ("rnb", "pop"):
            for essential in ("kick", "snare", "hihat", "bass", "synth"):
                if essential not in instruments:
                    instruments.append(essential)
            notes.append("Added full band for vocals.")
        elif genre == "lofi":
            for essential in ("kick", "snare", "hihat", "bass", "synth"):
                if essential not in instruments:
                    instruments.append(essential)
        elif genre == "hiphop":
            for essential in ("kick", "snare", "hihat", "bass"):
                if essential not in instruments:
                    instruments.append(essential)
        elif genre == "house":
            for essential in ("kick", "snare", "hihat", "bass", "synth"):
                if essential not in instruments:
                    instruments.append(essential)

    if "hihat" not in instruments and ("snare" in instruments or "kick" in instruments):
        instruments.append("hihat")

    seen: set[str] = set()
    instruments = [x for x in instruments if not (x in seen or seen.add(x))]

    bars_match = re.search(r"(\d+)\s*bar", lower)
    if bars_match:
        bars = max(4, min(32, int(bars_match.group(1))))

    if "sing" in lower or "vocal" in lower or "song" in lower:
        if mood == "energetic" and genre == "rnb":
            mood = "smooth"
            notes.append("Softened mood so the beat leaves room for vocals.")

    variation = zlib.adler32(prompt.strip().lower().encode()) & 0xFFFFFFFF

    spec = BeatSpec(
        genre=genre,
        bpm=bpm,
        key=key,
        scale=scale,
        instruments=instruments,
        bars=bars,
        mood=mood,
        variation=variation,
    )
    return spec, notes
