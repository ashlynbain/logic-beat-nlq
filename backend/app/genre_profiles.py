"""
Genre production stacks — distilled from common R&B, trap, house, and pop conventions.

References (high level):
- R&B / neo-soul: 85–105 BPM, sparse kick/snare, swung hats, sub + keys/pads, space for vocals
- Trap: 130–150 BPM (half-time feel), 808 sub, snare/clap on 2&4, triplet hi-hat rolls
- House: 120–128 BPM, four-on-the-floor kick, clap 2&4, offbeat hats, driving bass + stabs
- Pop: 100–125 BPM, straightforward backbeat, punchy kick, simple chord beds
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GenreProfile:
    name: str
    default_bpm: int
    bpm_range: tuple[int, int]
    default_instruments: tuple[str, ...]
    swing: float  # 0 = straight, ~0.66 = moderate shuffle
    kick_program: str
    bass_program: int
    synth_program: int
    bass_style: str  # root | eight_oh_eight | house_drive | pop_simple
    synth_style: str  # pad | stab | keys


PROFILES: dict[str, GenreProfile] = {
    "lofi": GenreProfile(
        name="Lo-Fi / Chillhop",
        default_bpm=78,
        bpm_range=(68, 92),
        default_instruments=("kick", "snare", "hihat", "bass", "synth"),
        swing=0.35,
        kick_program="lofi",
        bass_program=33,
        synth_program=88,  # Soft pad
        bass_style="lofi",
        synth_style="lofi_pad",
    ),
    "rnb": GenreProfile(
        name="R&B / Neo-Soul",
        default_bpm=94,
        bpm_range=(82, 105),
        default_instruments=("kick", "snare", "hihat", "bass", "synth"),
        swing=0.58,
        kick_program="sparse_syncopated",
        bass_program=33,  # Fingered electric bass
        synth_program=4,  # Electric piano / Rhodes feel
        bass_style="root",
        synth_style="keys",
    ),
    "hiphop": GenreProfile(
        name="Trap / Hip-Hop",
        default_bpm=140,
        bpm_range=(130, 160),
        default_instruments=("kick", "snare", "hihat", "bass", "perc"),
        swing=0.0,
        kick_program="trap",
        bass_program=38,  # Synth bass 1 (808-style in Logic)
        synth_program=80,  # Square lead for occasional accent — often minimal
        bass_style="eight_oh_eight",
        synth_style="stab",
    ),
    "house": GenreProfile(
        name="House / EDM",
        default_bpm=124,
        bpm_range=(118, 132),
        default_instruments=("kick", "snare", "hihat", "bass", "synth"),
        swing=0.0,
        kick_program="four_on_floor",
        bass_program=39,  # Synth bass 2
        synth_program=81,  # Saw lead — short stabs
        bass_style="house_drive",
        synth_style="stab",
    ),
    "pop": GenreProfile(
        name="Pop",
        default_bpm=118,
        bpm_range=(100, 128),
        default_instruments=("kick", "snare", "hihat", "bass", "synth"),
        swing=0.12,
        kick_program="backbeat",
        bass_program=33,
        synth_program=88,  # Warm pad
        bass_style="pop_simple",
        synth_style="pad",
    ),
}


def get_profile(genre: str) -> GenreProfile:
    return PROFILES.get(genre, PROFILES["pop"])
