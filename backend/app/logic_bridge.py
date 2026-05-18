import subprocess
import time
from pathlib import Path

from .logic_instruments import setup_instructions, tracks_for_spec
from .models import BeatSpec

LOGIC_APP_NAMES = ["Logic Pro", "Logic Pro X"]


def _logic_app_name() -> str:
    for name in LOGIC_APP_NAMES:
        script = f'tell application "System Events" to return exists application process "{name}"'
        result = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip().lower() == "true":
            return name
    return "Logic Pro"


def _write_setup_guide(output_dir: Path, spec: BeatSpec) -> Path:
    tracks = tracks_for_spec(spec.genre, spec.instruments)
    guide = setup_instructions(spec.genre, spec.bpm, tracks, spec.bars)
    path = output_dir / "LOGIC_SETUP.txt"
    path.write_text(guide, encoding="utf-8")
    return path


def open_in_logic(midi_path: Path, spec: BeatSpec, output_dir: Path) -> str:
    if not midi_path.exists():
        return "No MIDI file to open."

    app_name = _logic_app_name()
    setup_path = _write_setup_guide(output_dir, spec)

    subprocess.run(
        ["osascript", "-e", f'tell application "{app_name}" to activate'],
        check=False,
    )

    result = subprocess.run(
        ["open", "-a", app_name, str(midi_path.resolve())],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        return f"Could not open in {app_name}. Is Logic Pro installed?"

    time.sleep(1.5)
    _try_set_tempo(app_name, spec.bpm)

    tracks = tracks_for_spec(spec.genre, spec.instruments)
    track_list = ", ".join(t.midi_name for t in tracks)

    return (
        f"Opened beat_combined.mid in {app_name} ({track_list}) @ {spec.bpm} BPM. "
        f"In Logic: set cycle/loop to bars 1–{spec.bars}, enable cycle mode (C). "
        f"Match project tempo to {spec.bpm} BPM (click transport tempo). "
        f"If import asked to adapt tempo, choose Use MIDI file tempo. "
        f"Assign instruments — see {setup_path.name}. "
    )


def _try_set_tempo(app_name: str, bpm: int) -> None:
    """Best-effort: focus Logic; user may still need to confirm tempo."""
    script = f'''
tell application "{app_name}"
    activate
end tell
'''
    subprocess.run(["osascript", "-e", script], check=False)
