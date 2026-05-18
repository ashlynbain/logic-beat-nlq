"""Multiple drum templates per genre — rotated by bar index and variation seed."""

from __future__ import annotations

import random

from .models import BeatSpec

DrumBar = list[tuple[int, float, float, int]]

K, S, C, H, O, R, X = 36, 38, 39, 42, 46, 37, 54


def _hats_eighth(vel_on: int = 44, vel_off: int = 32) -> DrumBar:
    return [(H, i * 0.5, 0.04, vel_on if i % 2 else vel_off) for i in range(8)]


def _hats_lazy() -> DrumBar:
    return [(H, b, 0.04, v) for b, v in ((1.5, 28), (2.5, 32), (3.5, 26))]


_DRUM_POOLS: dict[str, list[DrumBar]] = {
    "lofi": [
        [(K, 0.0, 0.25, 58), (S, 1.0, 0.15, 48), (S, 3.0, 0.15, 50), *_hats_lazy()],
        [
            (K, 0.0, 0.2, 62),
            (K, 2.6, 0.12, 52),
            (R, 1.0, 0.1, 42),
            (R, 3.0, 0.1, 44),
            (H, 0.5, 0.03, 24),
            (H, 2.5, 0.03, 22),
        ],
        [(S, 1.0, 0.18, 46), (S, 3.0, 0.18, 48), (X, 0.5, 0.06, 22), (X, 1.5, 0.06, 20), (H, 2.0, 0.04, 30)],
        [(K, 0.0, 0.15, 55), (R, 1.0, 0.12, 50), (R, 3.0, 0.12, 52), (H, 1.0, 0.03, 26), (O, 3.25, 0.1, 32)],
    ],
    "sparse_syncopated": [
        [
            (K, 0.0, 0.2, 82),
            (K, 2.75, 0.15, 68),
            (S, 1.0, 0.2, 72),
            (S, 3.0, 0.2, 76),
            (C, 1.0, 0.15, 55),
            *_hats_eighth(),
        ],
        [
            (K, 0.0, 0.18, 78),
            (K, 1.5, 0.12, 62),
            (S, 1.0, 0.18, 70),
            (S, 3.0, 0.18, 74),
            (H, 0.5, 0.04, 36),
            (H, 1.5, 0.04, 42),
            (H, 2.5, 0.04, 36),
            (O, 3.5, 0.1, 40),
        ],
        [
            (K, 0.0, 0.22, 85),
            (S, 2.0, 0.1, 45),
            (S, 1.0, 0.2, 80),
            (S, 3.0, 0.2, 84),
            (X, 0.5, 0.05, 24),
            (X, 2.5, 0.05, 22),
            *_hats_eighth(38, 48),
        ],
    ],
    "trap": [
        [
            (K, 0.0, 0.1, 115),
            (K, 2.5, 0.08, 98),
            (S, 1.0, 0.12, 118),
            (S, 3.0, 0.12, 120),
            *_hats_eighth(55, 42),
        ],
        [
            (K, 0.0, 0.1, 110),
            (S, 1.0, 0.12, 115),
            (S, 3.0, 0.12, 118),
            (C, 1.0, 0.08, 88),
            *_hats_eighth(50, 38),
        ],
    ],
    "four_on_floor": [
        [(K, b, 0.08, 108) for b in (0.0, 1.0, 2.0, 3.0)]
        + [(C, b, 0.1, 92) for b in (1.0, 3.0)]
        + [(H, b, 0.05, 52) for b in (0.5, 1.5, 2.5, 3.5)],
        [(K, b, 0.08, 105) for b in (0.0, 1.0, 2.0, 3.0)]
        + [(S, 1.0, 0.1, 90), (S, 3.0, 0.1, 92)]
        + [(H, b, 0.05, 48) for b in (0.5, 1.5, 2.5, 3.5)]
        + [(O, 3.75, 0.1, 65)],
    ],
    "backbeat": [
        [
            (K, 0.0, 0.14, 98),
            (K, 2.0, 0.12, 88),
            (S, 1.0, 0.16, 90),
            (S, 3.0, 0.16, 94),
            *_hats_eighth(50, 38),
        ],
        [
            (K, 0.0, 0.15, 95),
            (S, 1.0, 0.14, 88),
            (S, 3.0, 0.14, 90),
            (H, 0.5, 0.04, 42),
            (H, 1.5, 0.04, 48),
            (H, 2.5, 0.04, 42),
            (H, 3.5, 0.04, 46),
        ],
    ],
}


def pick_drum_bar(kick_program: str, spec: BeatSpec, bar_index: int) -> DrumBar:
    rng = random.Random(spec.variation + bar_index * 17)
    pool = _DRUM_POOLS.get(kick_program, _DRUM_POOLS["backbeat"])
    idx = (spec.variation // 991 + bar_index + rng.randint(0, max(0, len(pool) - 1))) % len(pool)
    events = list(pool[idx])

    if spec.mood == "energetic":
        events = [(n, b, d, min(127, v + 12)) for n, b, d, v in events]
    elif spec.mood == "chill":
        events = [(n, b, d, max(18, v - 12)) for n, b, d, v in events]

    return events
