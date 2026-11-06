#!/bin/zsh
# Show Apple Wireless Direct Link (awdl0) state — NVIDIA cites this for Mac Wi-Fi GFN stutter.
set -euo pipefail
if ifconfig awdl0 >/dev/null 2>&1; then
  echo "=== awdl0 ==="
  ifconfig awdl0 | head -8
  if ifconfig awdl0 | grep -q 'status: active'; then
    echo
    echo "STATUS: UP/active — AirDrop/Continuity radio is live."
    echo "For a sticky suppress during GFN, install AWDL Control or Ping Warden."
    echo "  https://github.com/james-howard/AWDLControl"
  else
    echo
    echo "STATUS: present but not active"
  fi
else
  echo "awdl0 not found"
  exit 1
fi
