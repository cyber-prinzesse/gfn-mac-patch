#!/bin/zsh
# One-shot GFN play prep on Telekom Speedport (no Ethernet).
# 1) 10 Mbps telekom preset  2) AWDL down (admin)  3) channel gate  4) relaunch GFN
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== 1) GFN telekom preset (10 Mbps, HDR off) ==="
"$ROOT/bin/gfn-patch-settings.py" apply --preset telekom

echo
echo "=== 2) AWDL Off for this play session (AirDrop later: gfn-awdl-on.sh) ==="
osascript <<'EOF'
do shell script "pkill -9 -f 'ifconfig awdl0 down' 2>/dev/null || true; /sbin/ifconfig awdl0 down; (for i in $(seq 1 7200); do /sbin/ifconfig awdl0 down; /bin/sleep 1; done) &" with administrator privileges
EOF

echo
echo "=== 3) Wi-Fi DFS gate ==="
"$ROOT/bin/gfn-wifi-check.sh" || {
  echo
  echo ">>> Speedport still on DFS. Open admin and set 5 GHz → channel 44 @ 80 MHz:"
  echo "    http://192.168.2.1  →  WLAN / Funknetz  →  5 GHz  →  Kanal 44"
  open "http://192.168.2.1" 2>/dev/null || true
}

echo
echo "=== 4) Relaunch GeForce NOW ==="
osascript -e 'tell application "GeForceNOW" to quit' 2>/dev/null || true
sleep 2
pkill -x GeForceNOW 2>/dev/null || true
sleep 1
open -a GeForceNOW

echo
echo "Ready: start a game, play 15–20 min, then Help → Session report (Download > 0)."
echo "After play, restore AirDrop with: $ROOT/bin/gfn-awdl-on.sh"
