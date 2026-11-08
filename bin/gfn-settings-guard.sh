#!/bin/zsh
# Re-apply telekom preset while GFN is starting — it often nulls customProfile on launch.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PRESET="${1:-telekom}"
SECS="${2:-45}"
LOG="${GFN_DEBUG_LOG:-$HOME/.cursor/debug-321d63.log}"
end=$((SECONDS + SECS))
n=0
while (( SECONDS < end )); do
  n=$((n + 1))
  "$ROOT/bin/gfn-patch-settings.py" apply --preset "$PRESET" >/tmp/gfn-guard-last.txt 2>&1 || true
  python3 - <<PY
import json, time
from pathlib import Path
p = Path.home() / "Library/Application Support/NVIDIA/GeForceNOW/sharedstorage.json"
cfg = json.loads(p.read_text()).get("appSettingsConfig", {})
cp = cfg.get("customProfile") or {}
row = {
  "sessionId": "321d63",
  "runId": "settings-guard",
  "hypothesisId": "H4",
  "location": "gfn-settings-guard.sh",
  "message": "guard tick",
  "data": {
    "n": $n,
    "streamingProfiles": cfg.get("streamingProfiles"),
    "name": cp.get("name") if isinstance(cp, dict) else None,
    "maxBitrate": cp.get("maxBitrate") if isinstance(cp, dict) else None,
    "hdrStreamingMode": cp.get("hdrStreamingMode") if isinstance(cp, dict) else None,
    "width": cp.get("width") if isinstance(cp, dict) else None,
    "height": cp.get("height") if isinstance(cp, dict) else None,
    "custom_is_null": cfg.get("customProfile") is None,
  },
  "timestamp": int(time.time() * 1000),
}
with open("$LOG", "a") as f:
    f.write(json.dumps(row) + "\n")
print(row["data"])
PY
  sleep 3
done
echo "guard done ($n ticks)"
