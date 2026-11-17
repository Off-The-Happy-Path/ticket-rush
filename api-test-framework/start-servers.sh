#!/usr/bin/env bash
# Starts two ticket-rush instances: local (:8000, HOLD_SECONDS=2) and ci (:8001, HOLD_SECONDS=4).
# Usage: TICKET_RUSH=/path/to/ticket-rush ./start-servers.sh  (needs its demo-api venv)
set -e
TR="${TICKET_RUSH:-$(cd "$(dirname "$0")/.." && pwd)}/demo-api"
PY="${PYTHON:-$TR/.venv/Scripts/python.exe}"; [ -x "$PY" ] || PY="$TR/.venv/bin/python"
cd "$TR"
OVERSELL_BUG="${OVERSELL_BUG:-false}" ADMIN_ENABLED=true HOLD_SECONDS=2 "$PY" -m uvicorn app.main:app --port 8000 --log-level warning &
OVERSELL_BUG="${OVERSELL_BUG:-false}" ADMIN_ENABLED=true HOLD_SECONDS=4 "$PY" -m uvicorn app.main:app --port 8001 --log-level warning &
wait
