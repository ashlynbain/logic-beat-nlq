# Bloom Beats (Logic Beat NLQ)

Describe a beat in plain English → get a **~2 minute**, loop-ready **MIDI** file (`beat_combined.mid`) for vocals. Works with Logic Pro, GarageBand, FL Studio, Ableton, or any DAW.

Example: *Make me a beat for a great R&B song at 90 bpm*

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

## Static site + API

```bash
./scripts/build-public-html.sh
```

Upload `deploy/public_html/` to your web host. Set `config.json`:

```json
{ "apiBaseUrl": "https://your-api-server.com" }
```

On the API server: `export ALLOWED_ORIGINS=https://yourdomain.com`

Hosted builds auto-download `beat_combined.mid`. Run the backend on a VPS or your Mac with Python 3.10+.

## Using the MIDI

1. Open `beat_combined.mid` in your DAW.
2. Set tempo to the BPM from the app; loop bars 1–N (~2 minutes).
3. Assign instruments; record vocals.

Logic plugin notes: [docs/LOGIC_PRO_SETUP.md](docs/LOGIC_PRO_SETUP.md)

## Optional `.env` (API server)

See [.env.example](.env.example) for server-side OpenAI or Tavily fallbacks.

## License

MIT — see [LICENSE](LICENSE).
