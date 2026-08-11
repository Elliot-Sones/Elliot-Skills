#!/bin/zsh
# /comprend show brain [topic]
# Opens the live concept map. INVARIANT: never open the browser on an
# unverified URL. The exact URL must return HTTP 200 first; a dead, stale,
# or broken server gets killed and restarted before we give up.
PORT=8377
BASE="http://127.0.0.1:$PORT"
if [ -n "$1" ]; then
  topic=$(echo "$1" | tr '[:upper:] ' '[:lower:]-')
  URL="$BASE/?path=$topic"
else
  URL="$BASE/"
fi

start_server() {
  pkill -f "comprend/graph-server.py" 2>/dev/null
  nohup python3 ~/.claude/skills/comprend/graph-server.py >/dev/null 2>&1 &
  disown
  python3 - <<'EOF'
import socket, time, sys
for _ in range(60):
    try:
        socket.create_connection(("127.0.0.1", 8377), 0.3).close()
        sys.exit(0)
    except OSError:
        time.sleep(0.1)
sys.exit(1)
EOF
}

if ! nc -z 127.0.0.1 $PORT 2>/dev/null; then
  start_server || { echo "FAILED: server would not start"; exit 1; }
fi

# Verify the exact URL. A server that answers the port but 404s or errors is
# stale or broken: restart it once with current code, then re-verify.
if ! curl -sf -o /dev/null --max-time 5 "$URL"; then
  start_server || { echo "FAILED: server would not start"; exit 1; }
  if ! curl -sf -o /dev/null --max-time 5 "$URL"; then
    echo "FAILED: $URL not serving 200 even after restart"
    exit 1
  fi
fi

open "$URL"
echo "OPENED: $URL"
