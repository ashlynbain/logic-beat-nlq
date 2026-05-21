import os
import shutil
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .beat_engine import generate_beat
from .logic_bridge import open_in_logic
from .loop_length import apply_target_loop_length
from .lucky import roll_lucky_quest
from .models import BeatRequest, BeatResponse
from .prompt_normalize import normalize_prompt
from .prompt_resolve import resolve_beat_spec

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent.parent
OUTPUT_ROOT = PROJECT_ROOT / "output"
FRONTEND_DIST = PROJECT_ROOT / "frontend" / "dist"

app = FastAPI(title="Logic Beat NLQ", version="0.2.0")

def _cors_origins() -> list[str]:
    raw = os.getenv("ALLOWED_ORIGINS", "")
    if raw.strip():
        return [o.strip() for o in raw.split(",") if o.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "https://bloombeats.ashlynbain.com",
        "http://bloombeats.ashlynbain.com",
    ]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "parsing": {
            "default": "rule_based_keywords",
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
        },
    }


@app.post("/api/generate", response_model=BeatResponse)
def generate(request: BeatRequest):
    prompt = request.prompt.strip()
    bars = request.bars

    if request.lucky:
        prompt, lucky_variation = roll_lucky_quest()
        spec, adjustments = normalize_prompt(prompt, request.bars)
        spec.variation = lucky_variation
        adjustments.insert(
            0,
            f"Lucky roll — {spec.genre} at {spec.bpm} BPM, {spec.key} {spec.scale}, {spec.mood} mood.",
        )
    else:
        use_web = request.use_web_search or (
            request.client_keys is not None and request.client_keys.tavily_configured()
        ) or bool(os.getenv("TAVILY_API_KEY"))
        spec, adjustments, _web = resolve_beat_spec(
            prompt,
            request.bars,
            use_web_search=use_web,
            client_keys=request.client_keys,
        )

    apply_target_loop_length(spec, adjustments)

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
        message=logic_message
        or (
            "Beat generated. Download beat_combined.mid and open in any DAW "
            "(Logic, GarageBand, FL Studio, etc.)."
        ),
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
