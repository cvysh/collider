#!/usr/bin/env bash
# Start API + web for verification, killing anything we previously left behind.
#
#   ./scripts/serve.sh start   # (re)start both, waits until actually serving
#   ./scripts/serve.sh stop    # stop both
#
# Only processes matching this project's commands are killed, and the port is
# confirmed free before binding -- a stale server silently serving an old build
# is otherwise very easy to mistake for a bug in new code.
set -uo pipefail
cd "$(dirname "$0")/.."

API_PORT="${COLLIDER_API_PORT:-8123}"
WEB_PORT="${COLLIDER_WEB_PORT:-3100}"

free_port() {  # free_port <port> <pattern>
  local port=$1 pattern=$2 pid
  for pid in $(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null); do
    if ps -o command= -p "$pid" | grep -qE "$pattern"; then
      kill "$pid" 2>/dev/null
    else
      echo "port $port held by an unrelated process (pid $pid); not touching it" >&2
      return 1
    fi
  done
  for _ in $(seq 1 40); do
    lsof -nP -iTCP:"$port" -sTCP:LISTEN -t >/dev/null 2>&1 || return 0
    sleep 0.25
  done
  echo "port $port still busy" >&2
  return 1
}

stop() {
  free_port "$API_PORT" "uvicorn|collider.api" || true
  free_port "$WEB_PORT" "next|node" || true
  echo "stopped"
}

case "${1:-start}" in
  stop) stop ;;
  start)
    free_port "$API_PORT" "uvicorn|collider.api" || exit 1
    free_port "$WEB_PORT" "next|node" || exit 1

    .venv/bin/uvicorn collider.api.app:app --port "$API_PORT" --log-level warning \
      > /tmp/collider-api.log 2>&1 &
    for _ in $(seq 1 60); do
      curl -sf "http://127.0.0.1:${API_PORT}/api/health" >/dev/null && break
      sleep 0.25
    done

    ( cd web && COLLIDER_API_BASE="http://127.0.0.1:${API_PORT}" \
        npx next start --port "$WEB_PORT" > /tmp/collider-web.log 2>&1 & )
    for _ in $(seq 1 80); do
      curl -sf "http://127.0.0.1:${WEB_PORT}/" >/dev/null && break
      sleep 0.25
    done

    curl -sf "http://127.0.0.1:${API_PORT}/api/health" >/dev/null \
      && echo "api  ready on ${API_PORT}" || { echo "api FAILED"; tail -5 /tmp/collider-api.log; }
    curl -sf "http://127.0.0.1:${WEB_PORT}/" >/dev/null \
      && echo "web  ready on ${WEB_PORT}" || { echo "web FAILED"; tail -5 /tmp/collider-web.log; }
    ;;
  *) echo "usage: $0 [start|stop]"; exit 2 ;;
esac
