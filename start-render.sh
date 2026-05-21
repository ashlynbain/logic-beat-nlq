#!/usr/bin/env bash
# Use this as Render Start Command when Root Directory is blank (repo root).
set -euo pipefail
cd "$(dirname "$0")/backend"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
