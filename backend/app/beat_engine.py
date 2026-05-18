from __future__ import annotations

import random
from pathlib import Path

import mido

from .genre_profiles import GenreProfile, get_profile
from .logic_instruments import tracks_for_spec
from .midi_timing import (
    TimingContext,
    build_combined_file,
    quantize_beat,
    save_type0,
    total_beats,
    encode_drum_track,
    encode_melodic_track,
)
from .models import BeatSpec
from .music_theory import ChordEvent, bass_note_for_chord, progression_for_genre, voice_chord
from .pattern_variants import pick_drum_bar

DRUM_NOTES = {
    "kick": 36,
    "snare": 38,
    "clap": 39,
    "hihat": 42,
    "openhat": 46,
    "rim": 37,
    "shaker": 54,
}


def _rng(spec: BeatSpec) -> random.Random:
    return random.Random(spec.variation)


def _all_drums(profile: GenreProfile, spec: BeatSpec) -> list[tuple[int, float, float, int]]:
    rng = _rng(spec)
    loop_end = total_beats(spec.bars)
    out: list[tuple[int, float, float, int]] = []

    for bar in range(spec.bars):
        offset = bar * 4.0
        bar_events = pick_drum_bar(profile.kick_program, spec, bar)
        for note, beat, dur, vel in bar_events:
            start = quantize_beat(offset + beat)
            if start >= loop_end:
                continue
            end = min(start + dur, loop_end)
            v = max(1, min(127, vel + rng.randint(-6, 6)))
            out.append((note, start, max(0.05, end - start), v))

    if profile.kick_program == "trap":
        for bar in range(spec.bars):
            if (bar + spec.variation) % 2 == 1:
                base = bar * 4.0 + 3.0
                for i, t in enumerate([0.0, 0.25, 0.5, 0.75, 1.0]):
                    start = quantize_beat(base + t)
                    if start < loop_end:
                        out.append((DRUM_NOTES["hihat"], start, 0.03, 40 + i * 8))

    out.sort(key=lambda x: x[1])
    return out


def _bass_from_progression(
    spec: BeatSpec,
    profile: GenreProfile,
    progression: list[ChordEvent],
) -> list[tuple[float, float, int, int]]:
    notes: list[tuple[float, float, int, int]] = []
    octave = 1 if profile.bass_style == "eight_oh_eight" else 2

    for bar_idx, chord in enumerate(progression):
        bar_start = float(bar_idx * 4)
        root, fifth = bass_note_for_chord(spec.key, spec.scale, chord, octave)

        if profile.bass_style == "eight_oh_eight":
            notes.append((bar_start, 3.75, root, 108))
            if bar_idx % 2 == 1:
                notes.append((bar_start + 2.0, 1.5, fifth, 95))
        elif profile.bass_style == "house_drive":
            for step in range(8):
                t = bar_start + step * 0.5
                notes.append((t, 0.45, root, 90 if step % 2 == 0 else 74))
        elif profile.bass_style == "lofi":
            notes.append((bar_start, 3.5, root, 72))
            if (bar_idx + spec.variation) % 3 == 1:
                notes.append((bar_start + 2.0, 0.35, fifth, 58))
            if (bar_idx + spec.variation) % 4 == 2:
                notes.append((bar_start + 1.0, 0.25, root + 12, 48))
        elif profile.bass_style == "pop_simple":
            notes.append((bar_start, 0.95, root, 98))
            notes.append((bar_start + 2.0, 0.85, fifth, 90))
        else:
            notes.append((bar_start, 1.75, root, 88))
            notes.append((bar_start + 2.0, 1.75, fifth, 74))

    return notes


def _keys_from_progression(
    spec: BeatSpec,
    profile: GenreProfile,
    progression: list[ChordEvent],
) -> list[tuple[float, float, int, int]]:
    notes: list[tuple[float, float, int, int]] = []
    octave = 3 if profile.synth_style in ("keys", "lofi_pad", "pad") else 4

    for bar_idx, chord in enumerate(progression):
        bar_start = float(bar_idx * 4)
        voiced = voice_chord(spec.key, spec.scale, chord.root_degree, chord.quality, octave)

        if profile.synth_style == "stab":
            hits = (0.5, 1.5, 2.5, 3.5) if (spec.variation % 2) == 0 else (1.0, 3.0)
            for hit in hits:
                for i, n in enumerate(voiced[:3]):
                    notes.append((bar_start + hit, 0.2, n, 76 - i * 5))
        elif profile.synth_style == "lofi_pad":
            vel_base = 48 if spec.mood == "chill" else 54
            for i, n in enumerate(voiced):
                notes.append((bar_start, 3.5, n, vel_base - i * 3))
            if bar_idx % 4 == 3:
                notes.append((bar_start + 2.5, 0.75, voiced[-1] + 12, 38))
        elif profile.synth_style == "pad":
            for i, n in enumerate(voiced):
                notes.append((bar_start, 3.5, n, 52 - i * 3))
        else:
            for i, n in enumerate(voiced):
                notes.append((bar_start, 3.5, n, 60 - i * 4))

    return notes


def generate_beat(spec: BeatSpec, output_dir: Path) -> tuple[Path, dict[str, Path]]:
    profile = get_profile(spec.genre)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1) Lock one shared clock for the whole session (BPM, ticks, loop length)
    ctx = TimingContext.from_spec(spec)
    progression = progression_for_genre(spec.genre, spec.scale, spec.bars, spec.variation)
    logic_tracks = tracks_for_spec(spec.genre, spec.instruments)

    # 2) Compose all parts on that grid (event lists only — no files yet)
    drum_events: list[tuple[int, float, float, int]] = []
    bass_events: list[tuple[float, float, int, int]] = []
    key_events: list[tuple[float, float, int, int]] = []

    has_drums = any(i in spec.instruments for i in ("kick", "snare", "hihat", "perc", "openhat"))
    if has_drums:
        drum_events = _all_drums(profile, spec)
    if "bass" in spec.instruments:
        bass_events = _bass_from_progression(spec, profile, progression)
    if "synth" in spec.instruments:
        key_events = _keys_from_progression(spec, profile, progression)

    # 3) Encode MIDI tracks from the same TimingContext
    instrument_midis: list[mido.MidiTrack] = []
    track_paths: dict[str, Path] = {}

    if drum_events:
        drum_cfg = next((t for t in logic_tracks if t.is_drums), None)
        name = drum_cfg.midi_name if drum_cfg else "Drums"
        drum_track = encode_drum_track(ctx, name, drum_events)
        instrument_midis.append(drum_track)
        path = output_dir / "drums.mid"
        save_type0(ctx, drum_track, path)
        track_paths["drums"] = path

    if bass_events:
        bass_cfg = next((t for t in logic_tracks if t.midi_name in ("Bass", "808 Bass")), None)
        name = bass_cfg.midi_name if bass_cfg else "Bass"
        ch = bass_cfg.channel if bass_cfg else 0
        bass_track = encode_melodic_track(ctx, name, ch, bass_events)
        instrument_midis.append(bass_track)
        path = output_dir / "bass.mid"
        save_type0(ctx, bass_track, path)
        track_paths["bass"] = path

    if key_events:
        keys_cfg = next((t for t in logic_tracks if t.midi_name in ("Keys", "Synth", "Pads")), None)
        name = keys_cfg.midi_name if keys_cfg else "Keys"
        ch = keys_cfg.channel if keys_cfg else 1
        keys_track = encode_melodic_track(ctx, name, ch, key_events)
        instrument_midis.append(keys_track)
        path = output_dir / "keys.mid"
        save_type0(ctx, keys_track, path)
        track_paths["keys"] = path

    # 4) Combined file last — same tracks, same BPM on every lane
    combined_path = output_dir / "beat_combined.mid"
    build_combined_file(ctx, instrument_midis).save(combined_path)

    return combined_path, track_paths
