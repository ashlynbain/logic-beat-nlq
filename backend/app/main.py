import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .beat_engine import generate_beat
from .logic_bridge import open_in_logic
from .lucky import roll_lucky_bars, roll_lucky_quest
from .models import BeatRequest, BeatResponse
from .parser import parse_prompt_with_llm
from .prompt_normalize import normalize_prompt

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent.parent
OUTPUT_ROOT = PROJECT_ROOT / "output"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

app = FastAPI(title="Logic Beat NLQ", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/generate", response_model=BeatResponse)
def generate(request: BeatRequest):
    prompt = request.prompt.strip()
    bars = request.bars

    if request.lucky:
        prompt, lucky_variation = roll_lucky_quest()
        bars = roll_lucky_bars()
        spec, adjustments = normalize_prompt(prompt, bars)
        spec.bars = bars
        spec.variation = lucky_variation
        adjustments.insert(
            0,
            f"Lucky roll — {spec.genre} at {spec.bpm} BPM, {spec.key} {spec.scale}, {spec.mood} mood ({bars} bars).",
        )
    else:
        spec, adjustments = normalize_prompt(prompt, bars)
        spec.bars = bars

        llm_spec = parse_prompt_with_llm(prompt, bars)
        if llm_spec:
            spec = llm_spec
            spec.bars = bars
        if spec.variation == 0:
            import zlib

            spec.variation = zlib.adler32(prompt.lower().encode()) & 0xFFFFFFFF

    session_id = uuid.uuid4().hex[:12]
    session_dir = OUTPUT_ROOT / session_id

    try:
        combined_path, track_paths = generate_beat(spec, session_dir)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Beat generation failed: {exc}") from exc

    logic_message = ""
    if request.open_in_logic and combined_path.exists():
        logic_message = open_in_logic(combined_path, spec, session_dir)

    return BeatResponse(
        spec=spec,
        midi_path=str(combined_path.relative_to(PROJECT_ROOT)),
        track_paths={k: str(v.relative_to(PROJECT_ROOT)) for k, v in track_paths.items()},
        message=logic_message or "Beat generated. Open LOGIC_SETUP.txt in the output folder for instrument mapping.",
        adjustments=adjustments,
        original_prompt=prompt,
    )


@app.get("/api/download/{session_path:path}")
def download(session_path: str):
    file_path = (PROJECT_ROOT / session_path).resolve()
    if not str(file_path).startswith(str(OUTPUT_ROOT.resolve())):
        raise HTTPException(status_code=403, detail="Invalid path")
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, media_type="audio/midi", filename=file_path.name)


@app.delete("/api/session/{session_id}")
def cleanup_session(session_id: str):
    session_dir = OUTPUT_ROOT / session_id
    if session_dir.exists():
        shutil.rmtree(session_dir)
    return {"deleted": session_id}


if FRONTEND_DIST.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
