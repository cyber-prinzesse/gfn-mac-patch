#!/bin/zsh
# Wi-Fi-only prep for Telekom Speedport Smart 4 + GeForce NOW
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== GFN Telekom / Speedport prep (no Ethernet) ==="
"$ROOT/bin/gfn-awdl-status.sh" || true
echo
"$ROOT/bin/gfn-patch-settings.py" apply --preset bufferbloat
echo
echo "Opening Speedport admin — set 5 GHz channel to 44 @ 80 MHz,"
echo "and enable Priorisiertes WLAN for this Mac only."
open "http://speedport.ip" 2>/dev/null || open "http://192.168.2.1"
open -a "AWDLControl" 2>/dev/null || true
echo
echo "Then: quit/relaunch GeForce NOW, connect to VIP WLAN if you created it,"
echo "set AWDL Off, play, check Session report Download score."
