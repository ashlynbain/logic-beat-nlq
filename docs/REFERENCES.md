# References — libraries, tools, and repos

Everything this project depends on or was informed by, for later lookup.

---

## Core dependencies (this repo)

### Python (`backend/requirements.txt`)

| Package | Version | Role | Links |
|---------|---------|------|-------|
| **FastAPI** | ≥0.115 | HTTP API framework | https://fastapi.tiangolo.com/ · https://github.com/tiangolo/fastapi |
| **Uvicorn** | ≥0.32 | ASGI server (`uvicorn app.main:app`) | https://www.uvicorn.org/ · https://github.com/encode/uvicorn |
| **mido** | ≥1.3 | Read/write Standard MIDI Files | https://mido.readthedocs.io/ · https://github.com/mido/mido |
| **Pydantic** | ≥2.9 | Request/response models | https://docs.pydantic.dev/ · https://github.com/pydantic/pydantic |
| **python-multipart** | ≥0.0.12 | Form/file support for FastAPI | https://github.com/Kludex/python-multipart |
| **openai** | ≥1.54 | Optional NLQ parsing (`OPENAI_API_KEY`) | https://github.com/openai/openai-python · https://platform.openai.com/docs |

### JavaScript (`frontend/package.json`)

| Package | Version | Role | Links |
|---------|---------|------|-------|
| **React** | ^18.3 | UI | https://react.dev/ · https://github.com/facebook/react |
| **react-dom** | ^18.3 | DOM rendering | (same) |
| **Vite** | ^5.4 | Dev server & bundler | https://vite.dev/ · https://github.com/vitejs/vite |
| **@vitejs/plugin-react** | ^4.3 | React refresh in Vite | https://github.com/vitejs/vite-plugin-react |
| **TypeScript** | ^5.6 | Typing | https://www.typescriptlang.org/ |

### Fonts (loaded in `frontend/index.html`)

| Font | Use | Link |
|------|-----|------|
| **Press Start 2P** | Pixel headings, buttons | https://fonts.google.com/specimen/Press+Start+2P |
| **VT323** | Body / textarea | https://fonts.google.com/specimen/VT323 |

---

## Platform & DAW (not npm/pip packages)

| Tool | How we use it |
|------|----------------|
| **Apple Logic Pro** | Import `beat_combined.mid`, assign plugins, loop, record vocals |
| **macOS `open`** | `open -a "Logic Pro" <file.mid>` |
| **AppleScript / `osascript`** | Activate Logic (`logic_bridge.py`) |
| **General MIDI drum map** | Kick 36, snare 38, clap 39, closed hat 42, open hat 46 — via `mido` note numbers |

### Apple documentation (Logic)

- Logic Pro Scripter (in-plugin JavaScript MIDI): https://support.apple.com/guide/logicpro/scripter-api-overview-lgce3905a48c/mac
- Drum Kit Designer / Drum Machine Designer — assigned manually per `logic_instruments.py`

---

## External repos & articles (research / future work)

Not vendored in this project; cited for architecture decisions.

| Resource | Relevance |
|----------|-----------|
| [mido/mido](https://github.com/mido/mido) | MIDI file generation implementation |
| [MongLong0214/logic-pro-mcp](https://github.com/MongLong0214/logic-pro-mcp) | MCP API for Logic: `record_sequence`, `set_instrument`, tempo — possible future bridge |
| [PsychQuant/che-logic-pro-mcp](https://github.com/PsychQuant/che-logic-pro-mcp) | AppleScript-based Logic MCP (transport, tracks) |
| [aircrack-ng-debug/Logic-Pro-MCP](https://github.com/aircrack-ng-debug/Logic-Pro-MCP) | Related MCP effort |
| Logic Pro Help — MIDI import behavior | Informs “use MIDI file tempo” guidance |

### Production style references (genre conventions)

Inform `genre_profiles.py` and `music_theory.py` (BPM ranges, drum feel, progressions):

- Modern R&B / neo-soul: sparse drums, 85–105 BPM, space for vocals
- Trap: 130–150 BPM, 808 bass, hi-hat rolls, snare on 2 & 4
- House: four-on-the-floor kick ~124 BPM, offbeat hats
- Pop: backbeat kick/snare, simple harmonic beds

---

## Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | No | Enables optional cloud prompt parsing in `parser.py` |
| `OPENAI_MODEL` | No | Model name when API key is set (default `gpt-4o-mini`) |

---

## License note

This app’s code is project-local. Third-party packages retain their own licenses (MIT, Apache, etc.). Logic Pro is a commercial Apple product.
