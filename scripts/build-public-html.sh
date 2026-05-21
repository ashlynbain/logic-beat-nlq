#!/usr/bin/env bash
# Build frontend and copy to deploy/public_html for FTP/cPanel upload.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/deploy/public_html"

cd "$ROOT/frontend"
npm ci
VITE_AUTO_DOWNLOAD=true npm run build

rm -rf "$OUT"
mkdir -p "$OUT"
cp -R dist/* "$OUT/"
cp "$ROOT/deploy/htaccess.template" "$OUT/.htaccess"
cp "$ROOT/frontend/public/config.json" "$OUT/config.json"

echo ""
echo "Ready to upload: $OUT"
echo "Set apiBaseUrl in config.json to your API URL before upload."
