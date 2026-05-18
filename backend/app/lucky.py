"""Random beat quests — genre, BPM, mood, and key rolled for fun."""

from __future__ import annotations

import secrets

from .genre_profiles import PROFILES

_KEYS = ("C", "D", "E", "F", "G", "A", "B")
_MOODS = ("chill", "smooth", "energetic", "dreamy", "moody")
_BARS = (4, 8, 16)

_GENRE_PHRASES: dict[str, list[str]] = {
    "lofi": [
        "dusty lo-fi study beat",
        "chillhop groove with warm pads",
        "sleepy cassette-style lo-fi",
        "rainy window lo-fi instrumental",
    ],
    "rnb": [
        "smooth R&B bed for vocals",
        "neo soul groove with electric keys",
        "late-night R&B instrumental",
        "soulful R&B with space for singing",
    ],
    "hiphop": [
        "trap beat with heavy 808 and snare",
        "hard-hitting hip-hop instrumental",
        "dark trap with rolling hi-hats",
        "boom-bap style hip-hop beat",
    ],
    "house": [
        "four-on-the-floor house groove",
        "club house beat with driving bass",
        "uplifting house dance instrumental",
        "deep house rhythm for vocals",
    ],
    "pop": [
        "radio-ready pop instrumental",
        "catchy pop beat with bright chords",
        "upbeat pop backing track",
        "modern pop groove for singing",
    ],
}

_MOOD_WORDS: dict[str, str] = {
    "chill": "chill and laid back",
    "smooth": "smooth and warm",
    "energetic": "energetic and punchy",
    "dreamy": "dreamy and soft",
    "moody": "moody and dark",
}


def roll_lucky_quest() -> tuple[str, int]:
    """Return (prompt, variation_seed) for a random beat."""
    genre = secrets.choice(list(PROFILES.keys()))
    profile = PROFILES[genre]
    lo, hi = profile.bpm_range
    bpm = secrets.randbelow(hi - lo + 1) + lo

    mood = secrets.choice(_MOODS)
    key = secrets.choice(_KEYS)
    scale = secrets.choice(("minor", "major"))
    phrase = secrets.choice(_GENRE_PHRASES[genre])
    mood_text = _MOOD_WORDS[mood]

    # Explicit BPM in prompt so normalize respects the roll
    prompt = (
        f"{phrase}, {mood_text}, {key} {scale}, {bpm} bpm, "
        f"kick snare hihat bass synth for vocals"
    )
    variation = secrets.randbelow(2**32)
    return prompt, variation


def roll_lucky_bars() -> int:
    return secrets.choice(_BARS)
