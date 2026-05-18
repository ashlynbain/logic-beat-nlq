"""Chord progressions and voicings per genre — multiple templates per genre."""

from __future__ import annotations

from dataclasses import dataclass

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_INTERVALS = [0, 2, 4, 5, 7, 9, 11]
MINOR_INTERVALS = [0, 2, 3, 5, 7, 8, 10]


@dataclass(frozen=True)
class ChordEvent:
    root_degree: int
    quality: str  # min7 | maj7 | dom7 | min9 | sus2
    duration_beats: float = 4.0


def _root_semitone(key: str, scale: str, degree: int) -> int:
    k = NOTE_NAMES.index(key.upper())
    intervals = MAJOR_INTERVALS if scale == "major" else MINOR_INTERVALS
    return (k + intervals[degree % 7] + (degree // 7) * 12) % 12


def chord_pitch_classes(key: str, scale: str, root_degree: int, quality: str) -> list[int]:
    root = _root_semitone(key, scale, root_degree)
    if quality == "maj7":
        intervals = [0, 4, 7, 11]
    elif quality == "dom7":
        intervals = [0, 4, 7, 10]
    elif quality == "min9":
        intervals = [0, 3, 7, 10, 14]
    elif quality == "sus2":
        intervals = [0, 2, 7, 10]
    else:
        intervals = [0, 3, 7, 10]
    return [(root + i) % 12 for i in intervals]


def voice_chord(
    key: str,
    scale: str,
    root_degree: int,
    quality: str,
    base_octave: int = 3,
) -> list[int]:
    pcs = chord_pitch_classes(key, scale, root_degree, quality)
    order = [0, 2, 1, 3] if len(pcs) >= 4 else list(range(len(pcs)))
    notes = []
    octave = base_octave
    for pc_idx in order:
        pc = pcs[pc_idx]
        note = 12 * (octave + 1) + pc
        if notes and note <= notes[-1]:
            octave += 1
            note = 12 * (octave + 1) + pc
        notes.append(note)
    return notes


# (root_degree, quality) per bar in a 4-bar cycle
ProgressionTemplate = list[tuple[int, str]]

_PROGRESSIONS: dict[str, list[ProgressionTemplate]] = {
    "lofi": [
        [(0, "min7"), (5, "maj7"), (3, "maj7"), (4, "dom7")],
        [(0, "sus2"), (0, "min7"), (5, "maj7"), (3, "min7")],
        [(3, "min7"), (0, "min7"), (4, "dom7"), (5, "maj7")],
        [(0, "maj7"), (4, "dom7"), (3, "min7"), (0, "min9")],
    ],
    "rnb": [
        [(0, "min7"), (5, "maj7"), (3, "min7"), (4, "dom7")],
        [(0, "min7"), (3, "min7"), (5, "maj7"), (4, "dom7")],
        [(0, "min9"), (5, "maj7"), (0, "min7"), (4, "dom7")],
    ],
    "hiphop": [
        [(0, "min7"), (0, "min7"), (3, "min7"), (4, "dom7")],
        [(0, "min7"), (3, "min7"), (0, "min7"), (4, "dom7")],
        [(5, "maj7"), (0, "min7"), (3, "min7"), (0, "min7")],
    ],
    "house": [
        [(0, "min7"), (3, "min7"), (4, "dom7"), (0, "min7")],
        [(0, "min7"), (0, "min7"), (4, "dom7"), (3, "min7")],
    ],
    "pop": [
        [(0, "maj7"), (4, "maj7"), (5, "maj7"), (3, "min7")],
        [(0, "maj7"), (5, "maj7"), (3, "min7"), (4, "dom7")],
        [(0, "min7"), (5, "maj7"), (3, "min7"), (4, "dom7")],
    ],
}


def progression_for_genre(
    genre: str,
    scale: str,
    bars: int,
    variation: int = 0,
) -> list[ChordEvent]:
    templates = _PROGRESSIONS.get(genre, _PROGRESSIONS["pop"])
    template = templates[variation % len(templates)]

    # Major-key pop template swap when scale is major
    if genre == "pop" and scale == "major" and variation % 2 == 1:
        template = [(0, "maj7"), (5, "maj7"), (3, "min7"), (4, "dom7")]

    return [
        ChordEvent(template[bar % len(template)][0], template[bar % len(template)][1], 4.0)
        for bar in range(bars)
    ]


def bass_note_for_chord(
    key: str,
    scale: str,
    chord: ChordEvent,
    octave: int = 2,
) -> tuple[int, int]:
    root_pc = _root_semitone(key, scale, chord.root_degree)
    root = 12 * (octave + 1) + root_pc
    fifth_pc = (root_pc + 7) % 12
    fifth = 12 * (octave + 1) + fifth_pc
    return root, fifth
