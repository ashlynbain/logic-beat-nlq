"""Apply ~2 minute loop length from BPM."""

from __future__ import annotations

from .midi_timing import TARGET_LOOP_SECONDS, bars_for_duration, loop_duration_seconds
from .models import BeatSpec


def apply_target_loop_length(spec: BeatSpec, adjustments: list[str]) -> None:
    bars = bars_for_duration(spec.bpm)
    seconds = loop_duration_seconds(spec.bpm, bars)
    spec.bars = bars
    mins = int(seconds // 60)
    secs = int(round(seconds % 60))
    length_label = f"{mins}:{secs:02d}" if mins else f"{secs}s"
    adjustments.append(
        f"Loop ~{length_label} ({bars} bars @ {spec.bpm} BPM) for brainstorming / vocal practice."
    )
