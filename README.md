# Bloom Beats (Logic Beat NLQ)

Describe a beat in plain English → get a **~2 minute**, loop-ready **MIDI** file (`beat_combined.mid`) for vocals. Works with Logic Pro, GarageBand, FL Studio, Ableton, or any DAW.

Example: *Make me a beat for a great R&B song at 90 bpm*

## Try it live

See how it works: **[bloombeats.ashlynbain.com](https://bloombeats.ashlynbain.com/)**

## Features

- Rule-based parsing (no API keys required)
- Optional LLM keys in the UI (OpenAI, Anthropic, Google) — sent per request, never stored
- Optional Tavily key — used automatically when present
- ~2:00 loops, single combined MIDI download
- **I'm feeling lucky** random beat
- Static UI build for shared hosting; Python API on a separate host
- Logic Pro auto-open on local macOS

## Quick start

```bash
git clone https://github.com/ashlynbain/logic-beat-nlq.git
cd logic-beat-nlq

cd backend && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

cd ../frontend && npm install && npm run dev
```

Open **http://127.0.0.1:5173** or run `./scripts/dev.sh` from the project root.

## Production: bloombeats.ashlynbain.com

| URL | Role |
|-----|------|
| **https://bloombeats.ashlynbain.com** | Static UI (`public_html`) |
| **https://logic-beat-nlq.onrender.com** | Python API (FastAPI on Render) |

The UI uses that API when hosted on `bloombeats.ashlynbain.com`. Override in `config.json` if needed:

```json
{ "apiBaseUrl": "https://logic-beat-nlq.onrender.com" }
```

**1. UI (cPanel `public_html`)** — build and upload:

```bash
./scripts/build-public-html.sh
# upload deploy/public_html/* to bloombeats.ashlynbain.com
```

**2. API on Render** — use the repo’s `render.yaml`, or set manually:

| Render setting | Value |
|----------------|--------|
| **Root Directory** | `backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `bash start.sh` |
| **ALLOWED_ORIGINS** | `https://bloombeats.ashlynbain.com` |

If you see **`No module named 'app'`**, the start command ran from the wrong folder. Use **`bash start.sh`** with Root Directory **`backend`**, or from repo root:

- **Build:** `pip install -r backend/requirements.txt`
- **Start:** `bash start-render.sh`

Live API health check: `https://logic-beat-nlq.onrender.com/api/health`

## Using the MIDI

1. Open `beat_combined.mid` in your DAW.
2. Set tempo to the BPM from the app; loop bars 1–N (~2 minutes).
3. Assign instruments; record vocals.

Logic plugin notes: [docs/LOGIC_PRO_SETUP.md](docs/LOGIC_PRO_SETUP.md)

## Optional `.env` (API server)

See [.env.example](.env.example) for server-side OpenAI or Tavily fallbacks.

## License

MIT — see [LICENSE](LICENSE).
