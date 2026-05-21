# Deploy Bloom Beats to `public_html` (static UI)

The **website** (pixel UI) can live on shared hosting. The **beat engine** (Python/FastAPI) must run on a server that supports Python — your Mac, a VPS, or Railway/Render/Fly.io.

## What to upload

After building:

```bash
chmod +x scripts/build-public-html.sh
./scripts/build-public-html.sh
```

Upload **everything inside** `deploy/public_html/` to your host’s `public_html` folder (cPanel File Manager or FTP).

| File | Purpose |
|------|---------|
| `index.html` | App entry |
| `assets/*` | JS/CSS |
| `config.json` | **Edit this** — set your API URL |
| `.htaccess` | SPA routing (Apache) |

## 1. Point the UI at your API

On the server, edit `public_html/config.json`:

```json
{
  "apiBaseUrl": "https://api.yourdomain.com"
}
```

No trailing slash. Leave `""` only if the API is on the **same domain** under `/api` (uncommon on shared hosting).

Set CORS on the API server:

```bash
export ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 2. Run the backend somewhere

Example (VPS or your Mac):

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
ALLOWED_ORIGINS=https://yourdomain.com uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Put nginx/Caddy in front with HTTPS. Users enter **their own** OpenAI / Claude / Gemini / Tavily keys in the UI — you do not store keys on the server.

## 3. Downloads (hosted UI)

The `public_html` build sets **`VITE_AUTO_DOWNLOAD=true`**. After each successful quest, the browser automatically downloads **`beat_combined.mid`**. Users open that file in **any DAW** (Logic, GarageBand, FL Studio, Ableton, etc.).

“Open in Logic Pro” only appears in the **local Mac** dev build when the API is on the same machine.

## Local preview before upload

```bash
cd frontend && npm install && npm run dev
# UI: http://127.0.0.1:5173 — start backend on :8000 separately

# Or preview the production build:
npm run build && npm run preview
```

## User API keys (privacy)

- Keys are typed in the browser and held in React state only.
- Each generate request sends keys in JSON; the server uses them once and does not write them to disk or logs.
- Use **Clear all keys from memory** before closing the tab on a shared computer.
