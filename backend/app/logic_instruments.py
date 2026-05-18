"""
Logic Pro stock instrument mapping per track.
Track names are chosen so they're obvious in Logic's arrange window.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LogicTrackConfig:
    midi_name: str
    logic_plugin: str
    logic_category: str
    channel: int
    is_drums: bool = False


def tracks_for_spec(genre: str, instruments: list[str]) -> list[LogicTrackConfig]:
    """Ordered tracks for combined MIDI (drums first)."""
    out: list[LogicTrackConfig] = []

    drum_parts = [i for i in instruments if i in ("kick", "snare", "hihat", "perc", "openhat")]
    if drum_parts:
        kit = {
            "lofi": ("Drums", "Drum Kit Designer", "Drum Kit Designer"),
            "rnb": ("Drums", "Drum Kit Designer", "Drum Kit Designer"),
            "hiphop": ("Drums", "Drum Machine Designer", "Drum Machine Designer"),
            "house": ("Drums", "Drum Machine Designer", "Drum Machine Designer"),
            "pop": ("Drums", "Drum Kit Designer", "Drum Kit Designer"),
        }.get(genre, ("Drums", "Drum Kit Designer", "Drum Kit Designer"))
        out.append(
            LogicTrackConfig(
                midi_name=kit[0],
                logic_plugin=kit[1],
                logic_category=kit[2],
                channel=9,
                is_drums=True,
            )
        )

    if "bass" in instruments:
        bass = {
            "lofi": ("Bass", "Studio Bass", "Bass"),
            "rnb": ("Bass", "Studio Bass", "Bass"),
            "hiphop": ("808 Bass", "Studio Bass", "Bass"),
            "house": ("Bass", "Studio Bass", "Bass"),
            "pop": ("Bass", "Studio Bass", "Bass"),
        }.get(genre, ("Bass", "Studio Bass", "Bass"))
        out.append(
            LogicTrackConfig(
                midi_name=bass[0],
                logic_plugin=bass[1],
                logic_category=bass[2],
                channel=0,
            )
        )

    if "synth" in instruments:
        keys = {
            "lofi": ("Pads", "Alchemy", "Synthesizer"),
            "rnb": ("Keys", "Vintage Electric Piano", "Keyboards"),
            "hiphop": ("Keys", "Vintage Electric Piano", "Keyboards"),
            "house": ("Synth", "Retro Synth", "Synthesizer"),
            "pop": ("Keys", "Vintage Electric Piano", "Keyboards"),
        }.get(genre, ("Keys", "Vintage Electric Piano", "Keyboards"))
        out.append(
            LogicTrackConfig(
                midi_name=keys[0],
                logic_plugin=keys[1],
                logic_category=keys[2],
                channel=1,
            )
        )

    return out


def setup_instructions(genre: str, bpm: int, tracks: list[LogicTrackConfig], bars: int = 8) -> str:
    lines = [
        f"1. Set project tempo to {bpm} BPM (transport bar — must match MIDI or loop will feel wrong).",
        f"2. Enable cycle/loop: drag cycle strip over bars 1–{bars}, press C for cycle mode.",
        "3. If Logic asked when importing: choose Use MIDI file tempo / Do not adapt.",
        "4. For each track: select it → press 'i' → instrument slot → load:",
        "",
    ]
    for i, t in enumerate(tracks, 1):
        lines.append(f"   Track '{t.midi_name}' → {t.logic_category} → {t.logic_plugin}")
    tips = {
        "lofi": (
            "5. Drums: mellow lo-fi kit. Pads: Alchemy soft wash + tape delay. "
            "Heavy low-pass on hats in mix."
        ),
        "rnb": (
            "5. Drums: Neo Soul kit. Keys: Mercury Rhodes on Vintage Electric Piano."
        ),
        "hiphop": "5. Drums: TR-808 style. Bass: 808 sub.",
        "house": "5. Four-on-the-floor mix. Short synth stabs.",
        "pop": "5. Punchy kit, warm keys pad.",
    }
    lines.extend(["", tips.get(genre, tips["pop"]), "6. Add Audio track for vocals."])
    return "\n".join(lines)
