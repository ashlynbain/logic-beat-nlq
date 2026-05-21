# Bloom Beats (Logic Beat NLQ)

Describe a beat in plain English → get a **~2 minute**, loop-ready **MIDI** file (`beat_combined.mid`) for vocals. Works with **Logic Pro**, **GarageBand**, FL Studio, Ableton, or any DAW.

**Docs:** [Architecture](docs/ARCHITECTURE.md) · [Deploy static site](docs/DEPLOY_PUBLIC_HTML.md) · [Logic Pro setup](docs/LOGIC_PRO_SETUP.md) · [References](docs/REFERENCES.md)

Example prompt:

> Make me a beat for a great R&B song at 90 bpm

## Features

| Feature | Description |
|---------|-------------|
| **Rule-based parsing** | Default — keywords for genre, BPM, key, mood (no API keys required) |
| **Bring your own LLM** | Paste **OpenAI**, **Anthropic (Claude)**, or **Google (Gemini)** keys in the UI — used once per request, **never stored** |
| **Tavily (optional)** | Paste a Tavily key — web context is fetched automatically when a key is present |
| **~2:00 loops** | Bar count is computed from BPM so each beat is ~2 minutes for brainstorming |
| **Single download** | `beat_combined.mid` only (drums + bass + keys) |
| **I'm feeling lucky** | Random genre, BPM, key, and mood |
| **Static hosting** | Build UI for `public_html`; API runs on a separate Python host |
| **Logic Pro (local)** | Optional one-click open on macOS when API runs locally |

## How it works

1. **Parse** — `prompt_normalize.py` (rules) and/or your LLM + optional Tavily → `BeatSpec`
2. **Generate** — `beat_engine.py` — genre patterns, chords, shared `TimingContext` → MIDI
3. **Deliver** — Download or open `beat_combined.mid` in a DAW

## Requirements

**Local full stack**

- macOS for Logic Pro auto-open (optional)
- Python 3.10+
- Node.js 18+

**Hosted UI only**

- Any static host (`public_html`) + a Python server for the API (see [docs/DEPLOY_PUBLIC_HTML.md](docs/DEPLOY_PUBLIC_HTML.md))

## Quick start (fork & run locally)

```bash
git clone https://github.com/ashlynbain/logic-beat-nlq.git
cd logic-beat-nlq

# Backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173** → enter a prompt → **Start quest**.

Both at once:

```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

## API keys (optional, browser-only)

In **Quest settings**, users can paste keys for smarter parsing. Keys are sent in the JSON body of `/api/generate` and are **not written to disk** on the server.

| Provider | UI field | Default model |
|----------|----------|----------------|
| OpenAI | GPT | `gpt-4o-mini` |
| Anthropic | Claude | `claude-3-5-haiku-20241022` |
| Google | Gemini | `gemini-1.5-flash` |
| Tavily | Web context | runs automatically if key is set |

Server-side fallbacks (optional `.env` on the API host): see [.env.example](.env.example).

## Deploy UI to shared hosting

```bash
./scripts/build-public-html.sh
```

Upload `deploy/public_html/` to your host. Edit `config.json` with your API URL. Details: [docs/DEPLOY_PUBLIC_HTML.md](docs/DEPLOY_PUBLIC_HTML.md).

Set on the API server:

```bash
export ALLOWED_ORIGINS=https://yourdomain.com
```

## Using the MIDI file

1. Download **`beat_combined.mid`** (auto-download on hosted builds).
2. Open in your DAW; set tempo to the BPM shown in the app.
3. Loop bars **1–N** (N = bar count shown; ~2 minutes total).
4. Assign drum/bass/synth sounds (MIDI has no built-in instruments).
5. Record vocals on an audio track.

Logic-specific plugin tips: [docs/LOGIC_PRO_SETUP.md](docs/LOGIC_PRO_SETUP.md).

## Prompt tips

| Say this… | Gets you… |
|-----------|-----------|
| `120 bpm` | Tempo |
| `rnb`, `neo soul`, `lo-fi`, `trap` | Genre feel |
| `synth, bass, snare` | Instruments |
| `A minor`, `chill` | Key and mood |
| Vague / artist references | Use an LLM + optional Tavily key |

## Project layout

```
backend/app/     FastAPI, beat engine, parsers, LLM providers
frontend/        React + Vite UI
scripts/         dev.sh, build-public-html.sh
docs/            Architecture, deploy, Logic setup
deploy/          htaccess template (built site output in public_html/)
```

## License

MIT — see [LICENSE](LICENSE).
