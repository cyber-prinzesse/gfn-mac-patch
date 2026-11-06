#!/bin/zsh
# Fail loudly if MagentaWLAN is still on a DFS channel (100+) — GFN Download≈0 risk.
set -euo pipefail
LOG="${GFN_DEBUG_LOG:-$HOME/.cursor/debug-321d63.log}"
OUT=$(system_profiler SPAirPortDataType 2>/dev/null | sed -n '/Current Network Information:/,/Other Local Wi-Fi/p')
CHANNEL_LINE=$(print -r -- "$OUT" | grep -E 'Channel:' | head -1 | sed 's/^[[:space:]]*//')
CHAN_NUM=$(print -r -- "$CHANNEL_LINE" | grep -oE '[0-9]+' | head -1)

python3 - "$CHAN_NUM" "$CHANNEL_LINE" "$LOG" <<'PY'
import json, sys, time
chan, line, log = sys.argv[1], sys.argv[2], sys.argv[3]
chan_i = int(chan) if chan.isdigit() else -1
dfs = chan_i >= 100
row = {
  "sessionId": "321d63",
  "runId": "wifi-check",
  "hypothesisId": "H1",
  "location": "gfn-wifi-check.sh",
  "message": "DFS channel gate",
  "data": {"channel": chan_i, "channel_line": line, "dfs": dfs, "ok": not dfs and chan_i > 0},
  "timestamp": int(time.time() * 1000),
}
with open(log, "a") as f:
    f.write(json.dumps(row) + "\n")
print(line or "Channel: (unknown)")
if dfs:
    print("FAIL: still on DFS channel — set Speedport 5 GHz to 44 @ 80 MHz (not 100+).", file=sys.stderr)
    sys.exit(2)
if chan_i <= 0:
    print("WARN: could not read channel", file=sys.stderr)
    sys.exit(1)
print("OK: non-DFS channel")
PY
