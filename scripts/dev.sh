#!/usr/bin/env bash
# Run the API and the web app together for local development.
#
#   ./scripts/dev.sh
#
# Stops both on Ctrl-C.
set -euo pipefail
cd "$(dirname "$0")/.."

PORT="${COLLIDER_API_PORT:-8123}"
export COLLIDER_API_BASE="http://127.0.0.1:${PORT}"

.venv/bin/uvicorn collider.api.app:app --port "$PORT" --reload &
API_PID=$!
trap 'kill $API_PID 2>/dev/null || true' EXIT

until curl -sf "http://127.0.0.1:${PORT}/api/health" >/dev/null; do sleep 0.3; done
echo "API ready on ${PORT}"

cd web && npm run dev
