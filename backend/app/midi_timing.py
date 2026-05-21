"""Shared BPM / grid and absolute-tick MIDI encoding — all tracks stay locked."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mido

from .models import BeatSpec

GRID_TICKS = 120  # 16th notes at 480 TPQ


@dataclass(frozen=True)
class TimingContext:
    """Single clock for an entire beat generation session."""

    tpq: int
    bpm: int
    tempo_us: int
    loop_ticks: int
    bars: int

    @classmethod
    def from_spec(cls, spec: BeatSpec) -> TimingContext:
        tpq = 480
        return cls(
            tpq=tpq,
            bpm=spec.bpm,
            tempo_us=int(60_000_000 / spec.bpm),
            loop_ticks=int(total_beats(spec.bars) * tpq),
            bars=spec.bars,
        )


TARGET_LOOP_SECONDS = 120.0  # ~2 minute brainstorming loop


def total_beats(bars: int) -> float:
    return bars * 4.0


def bars_for_duration(bpm: int, seconds: float = TARGET_LOOP_SECONDS) -> int:
    """4/4 loop length: seconds = bars × 4 × (60 / bpm)."""
    if bpm < 1:
        bpm = 120
    bars = round(seconds * bpm / 240.0)
    return max(16, min(128, bars))


def loop_duration_seconds(bpm: int, bars: int) -> float:
    return bars * 240.0 / max(bpm, 1)


def quantize_beat(beat: float, tpq: int = 480, grid: int = GRID_TICKS) -> float:
    tick = round(beat * tpq / grid) * grid
    return tick / tpq


def _beat_to_tick(beat: float, tpq: int) -> int:
    return int(round(quantize_beat(beat, tpq) * tpq))


def _schedule_note_events(
    ctx: TimingContext,
    events: list[tuple[float, float, int, int]],
) -> list[tuple[int, str, int, int]]:
    """(beat, duration, note, velocity) → sorted absolute (tick, on|off, note, vel)."""
    scheduled: list[tuple[int, str, int, int]] = []
    for beat, dur, note, vel in events:
        start_tick = _beat_to_tick(beat, ctx.tpq)
        if start_tick >= ctx.loop_ticks:
            continue
        dur_ticks = max(1, int(round(max(1 / ctx.tpq, dur) * ctx.tpq)))
        end_tick = min(start_tick + dur_ticks, ctx.loop_ticks)
        scheduled.append((start_tick, "on", note, vel))
        scheduled.append((end_tick, "off", note, 0))
    scheduled.sort(key=lambda x: (x[0], 0 if x[1] == "on" else 1))
    return scheduled


def _schedule_drum_events(
    ctx: TimingContext,
    events: list[tuple[int, float, float, int]],
) -> list[tuple[int, str, int, int]]:
    melodic = [(beat, dur, note, vel) for note, beat, dur, vel in events]
    return _schedule_note_events(ctx, melodic)


def _ticks_to_delta_track(
    ctx: TimingContext,
    name: str,
    scheduled: list[tuple[int, str, int, int]],
) -> mido.MidiTrack:
    track = mido.MidiTrack()
    track.append(mido.MetaMessage("track_name", name=name, time=0))
    cumulative = 0
    for tick, kind, note, vel in scheduled:
        delta = max(0, tick - cumulative)
        if kind == "on":
            track.append(
                mido.Message("note_on", channel=0, note=note, velocity=vel, time=delta)
            )
        else:
            track.append(
                mido.Message("note_off", channel=0, note=note, velocity=0, time=delta)
            )
        cumulative = tick
    track.append(mido.MetaMessage("end_of_track", time=max(0, ctx.loop_ticks - cumulative)))
    return track


def encode_melodic_track(
    ctx: TimingContext,
    name: str,
    channel: int,
    events: list[tuple[float, float, int, int]],
) -> mido.MidiTrack:
    scheduled = _schedule_note_events(ctx, events)
    track = _ticks_to_delta_track(ctx, name, scheduled)
    for msg in track:
        if msg.type in ("note_on", "note_off"):
            msg.channel = channel
    return track


def encode_drum_track(
    ctx: TimingContext,
    name: str,
    events: list[tuple[int, float, float, int]],
) -> mido.MidiTrack:
    scheduled = _schedule_drum_events(ctx, events)
    track = _ticks_to_delta_track(ctx, name, scheduled)
    for msg in track:
        if msg.type in ("note_on", "note_off"):
            msg.channel = 9
    return track


def build_conductor_track(ctx: TimingContext) -> mido.MidiTrack:
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("set_tempo", tempo=ctx.tempo_us, time=0))
    meta.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    meta.append(
        mido.MetaMessage(
            "marker",
            text=f"Loop {ctx.bars} bars @ {ctx.bpm} BPM",
            time=0,
        )
    )
    meta.append(mido.MetaMessage("end_of_track", time=ctx.loop_ticks))
    return meta


def prepend_tempo_meta(ctx: TimingContext, track: mido.MidiTrack) -> mido.MidiTrack:
    """Type-1 instrument tracks: duplicate tempo so Logic aligns every lane."""
    out = mido.MidiTrack()
    out.append(mido.MetaMessage("set_tempo", tempo=ctx.tempo_us, time=0))
    out.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
    for msg in track:
        if msg.type in ("end_of_track",):
            continue
        out.append(msg.copy(time=msg.time))
    # Re-pad to exact loop length
    length = sum(m.time for m in out)
    out.append(mido.MetaMessage("end_of_track", time=max(0, ctx.loop_ticks - length)))
    return out


def save_type0(ctx: TimingContext, track: mido.MidiTrack, path: Path) -> None:
    """Standalone file: one track with tempo + notes (same BPM as session)."""
    merged = prepend_tempo_meta(ctx, track)
    mid = mido.MidiFile(type=0, ticks_per_beat=ctx.tpq)
    mid.tracks.append(merged)
    mid.save(path)


def build_combined_file(ctx: TimingContext, instrument_tracks: list[mido.MidiTrack]) -> mido.MidiFile:
    mid = mido.MidiFile(type=1, ticks_per_beat=ctx.tpq)
    mid.tracks.append(build_conductor_track(ctx))
    for t in instrument_tracks:
        mid.tracks.append(prepend_tempo_meta(ctx, t))
    return mid
