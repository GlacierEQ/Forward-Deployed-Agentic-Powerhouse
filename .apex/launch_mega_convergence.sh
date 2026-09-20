#!/usr/bin/env bash
set -euo pipefail

BASE="/root/.apex"
mkdir -p "$BASE/logs" "$BASE/state"

PIDFILE="$BASE/state/mega_supervisor.pid"

if [[ -f "$PIDFILE" ]]; then
    pid=$(cat "$PIDFILE" 2>/dev/null || true)
    if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
        echo "MEGA_SUPERVISOR_ALREADY_RUNNING pid=$pid"
        exit 0
    fi
fi

echo "Launching APEX Tri-Pillar Mega Convergence Daemon with setsid..."
nohup setsid python3 "$BASE/mega_supervisor.py" >> "$BASE/logs/mega_supervisor.log" 2>&1 </dev/null &
pid=$!
echo "$pid" > "$PIDFILE"

sleep 2
if kill -0 "$pid" 2>/dev/null; then
    echo "MEGA_SUPERVISOR_STARTED pid=$pid"
else
    echo "MEGA_SUPERVISOR_FAILED_TO_START"
    tail -n 30 "$BASE/logs/mega_supervisor.log" || true
    exit 1
fi
