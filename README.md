# Bloom Beats (Logic Beat NLQ)

Describe a beat in plain English → get MIDI tracks you can open in **Logic Pro** and sing over.

**Documentation:** [docs/README.md](docs/README.md) · [Architecture](docs/ARCHITECTURE.md) · [References](docs/REFERENCES.md) · [Logic Pro setup](docs/LOGIC_PRO_SETUP.md)

Example prompt:

> Make me a beat for a great R&B song at 90 bpm

## How it works

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Web UI     │────▶│  NLQ Parser  │────▶│ Beat Engine │────▶│  MIDI files  │
│  (prompt)   │     │  (BPM, genre │     │  (patterns) │     │  per track   │
└─────────────┘     │   instruments)│     └─────────────┘     └──────┬───────┘
                    └──────────────┘                                  │
                                                                      ▼
                                                              ┌──────────────┐
                                                              │ Logic Pro    │
                                                              │ (open/import)│
                                                              └──────────────┘
```

1. **Parser** — `prompt_normalize.py` (and optional `parser.py` if configured) → `BeatSpec`.
2. **Beat engine** — Genre patterns, chord progression, loop-aligned MIDI (`beat_combined.mid`).
3. **Logic bridge** — Opens combined MIDI in Logic Pro; writes `LOGIC_SETUP.txt` (macOS `open` + AppleScript).

## Requirements

- macOS with **Logic Pro** (or Logic Pro X)
- Python 3.10+
- Node.js 18+

Optional environment variables are documented in `.env.example` (not required for local use).

## Quick start

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

Open **http://127.0.0.1:5173**, enter a prompt, click **Start quest**.

Or run both at once:

```bash
chmod +x scripts/dev.sh
./scripts/dev.sh
```

## Using in Logic Pro

After generation:

1. Logic opens **`beat_combined.mid`** (Drums, Bass, Keys tracks).
2. Set project tempo to the BPM shown in the UI; enable **cycle loop** over bars 1–N.
3. Assign instruments — see [docs/LOGIC_PRO_SETUP.md](docs/LOGIC_PRO_SETUP.md).
4. Add an **audio track** for vocals and record.

## Prompt tips

| Say this… | Gets you… |
|-----------|-----------|
| `120 bpm` | Tempo |
| `rnb`, `neo soul`, `lo-fi` | Genre feel |
| `synth, bass, snare` | Those tracks |
| `A minor`, `chill` | Key and softer patterns |
| `energetic`, `140 bpm` | Busier hats, stronger velocity |

## Roadmap

- [ ] Single Logic project with pre-mapped tracks
- [ ] Audio preview in the browser
- [ ] More genre pattern libraries
- [ ] Vocal guide key / scale overlay track

## Limitations

Apple does not expose a full public API for Logic Pro. This app generates **MIDI** and opens files in Logic; you assign plugins and mix.

## License

MIT — see [LICENSE](LICENSE).
