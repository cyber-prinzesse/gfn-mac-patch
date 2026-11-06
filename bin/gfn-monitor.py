#!/usr/bin/env python3
"""GFN session monitor — NDJSON samples for AWDL / Wi-Fi / ICMP / GFN logs.

Hypotheses (hypothesisId in each row):
  A — awdl0 UP causes Wi-Fi spikes / loss during play
  B — latency under load / jitter spikes (bufferbloat) during stream
  C — stream profile (HDR / uncapped bitrate / high res) correlates with degradation
  D — background CPU/net load during session
  E — GFN client logs report packet loss / bitrate drops
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

GFN = Path.home() / "Library/Application Support/NVIDIA/GeForceNOW"
DEFAULT_OUT = Path.home() / ".cursor" / "gfn-session.ndjson"


def emit(path: Path, hypothesis_id: str, location: str, message: str, data: dict, run_id: str, session_id: str | None) -> None:
    row = {
        "runId": run_id,
        "hypothesisId": hypothesis_id,
        "location": location,
        "message": message,
        "data": data,
        "timestamp": int(time.time() * 1000),
    }
    if session_id:
        row["sessionId"] = session_id
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def sh(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL, timeout=8)
    except Exception:
        return ""


def awdl_state() -> dict:
    out = sh("ifconfig awdl0 2>/dev/null")
    up = "status: active" in out or ("RUNNING" in out and out.startswith("awdl0:") and "UP" in out.split("\n")[0])
    return {"awdl_up": up, "flags_line": (out.split("\n")[0] if out else "")}


def wifi_state() -> dict:
    sp = sh(
        "system_profiler SPAirPortDataType 2>/dev/null | "
        "awk '/Status: Connected/{c=1} c&&/PHY Mode|Channel|Signal \\/ Noise|Transmit Rate|MCS Index/{print; if(++n>=5) exit}'"
    )
    d: dict = {"raw": sp.strip()[:400]}
    m = re.search(r"Channel:\s*(\d+)\s*\(([^)]+)\)", sp)
    if m:
        d["channel"] = int(m.group(1))
        d["band"] = m.group(2)
    m = re.search(r"Signal / Noise:\s*(-?\d+)\s*dBm\s*/\s*(-?\d+)\s*dBm", sp)
    if m:
        d["rssi"] = int(m.group(1))
        d["noise"] = int(m.group(2))
    m = re.search(r"Transmit Rate:\s*(\d+)", sp)
    if m:
        d["tx_mbps"] = int(m.group(1))
    return d


def ping_sample(host: str, count: int = 5) -> dict:
    out = sh(f"ping -c {count} -W 1000 {host} 2>/dev/null")
    sent = recv = loss = None
    rtt_avg = rtt_dev = None
    m = re.search(r"(\d+) packets transmitted, (\d+) packets received, ([0-9.]+)% packet loss", out)
    if m:
        sent, recv, loss = int(m.group(1)), int(m.group(2)), float(m.group(3))
    m = re.search(r"round-trip min/avg/max/(?:stddev|std-dev) = ([0-9.]+)/([0-9.]+)/([0-9.]+)/([0-9.]+)", out)
    if m:
        rtt_avg = float(m.group(2))
        rtt_dev = float(m.group(4))
    return {"host": host, "sent": sent, "recv": recv, "loss_pct": loss, "rtt_avg_ms": rtt_avg, "rtt_dev_ms": rtt_dev}


def gfn_running() -> bool:
    return "GeForceNOW.app/Contents/MacOS/GeForceNOW" in sh("ps -axo command=")


def gfn_profile() -> dict:
    p = GFN / "sharedstorage.json"
    if not p.exists():
        return {"missing": True}
    try:
        d = json.loads(p.read_text())
        cfg = d.get("appSettingsConfig", {})
        custom = cfg.get("customProfile", {})
        return {
            "streamingProfiles": cfg.get("streamingProfiles"),
            "fps": custom.get("fps"),
            "hdrStreaming": custom.get("hdrStreaming"),
            "maxBitrate": custom.get("maxBitrate"),
            "maxBitrateAuto": custom.get("maxBitrateAuto"),
            "maxPacketSize": custom.get("maxPacketSize"),
            "reflex": custom.get("reflex"),
            "bitDepth": custom.get("bitDepth"),
            "primaryDisplayResolution": custom.get("primaryDisplayResolution"),
            "sessionId": (d.get("streamingSessionId") or {}).get("sessionId"),
        }
    except Exception as e:
        return {"error": str(e)}


def gfn_log_signals() -> dict:
    hits = []
    patterns = re.compile(
        r"packet.?loss|PacketLoss|jitter|bitrate|NetworkQuality|congestion|lost.?frame|frame.?drop|RTT|latency",
        re.I,
    )
    for name in ("debug.log", "logs/gfn_reliability_monitor.log", "logs/gameStreamClientAgent.log"):
        path = GFN / name
        if not path.exists():
            continue
        try:
            data = path.read_bytes()[-80000:].decode("utf-8", "replace")
            for line in data.splitlines()[-200:]:
                if patterns.search(line):
                    hits.append({"file": name, "line": line.strip()[:240]})
        except Exception:
            continue
    return {"hit_count": len(hits), "samples": hits[-8:]}


def netstat_udp_gfn() -> dict:
    out = sh("netstat -an -p udp 2>/dev/null | rg '4900[3-6]|\\.4900[3-6]' || true")
    lines = [L.strip() for L in out.splitlines() if L.strip()]
    return {"udp_gfn_lines": lines[:20], "count": len(lines)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--duration", type=float, default=900, help="seconds to run (default 900)")
    ap.add_argument("--interval", type=float, default=2, help="sample interval seconds")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT, help="NDJSON output path")
    ap.add_argument("--ping-host", default="1.1.1.1")
    ap.add_argument("--run-id", default="session")
    ap.add_argument(
        "--cursor-debug",
        metavar="SESSION",
        help="also mirror rows into ~/.cursor/debug-<SESSION>.log with sessionId set",
    )
    args = ap.parse_args()

    outs = [args.out]
    session_id = None
    if args.cursor_debug:
        session_id = args.cursor_debug
        outs.append(Path.home() / ".cursor" / f"debug-{session_id}.log")

    def log(hid, loc, msg, data):
        for out in outs:
            emit(out, hid, loc, msg, data, args.run_id, session_id if out.name.startswith("debug-") else None)

    log("C", "gfn-monitor.py:start", "monitor start", {
        "profile": gfn_profile(),
        "gfn_running": gfn_running(),
        "interval": args.interval,
        "duration": args.duration,
        "out": str(args.out),
    })
    log("A", "gfn-monitor.py:awdl0", "awdl baseline", awdl_state())
    log("C", "gfn-monitor.py:wifi0", "wifi baseline", wifi_state())

    t0 = time.time()
    n = 0
    while time.time() - t0 < args.duration:
        n += 1
        a = awdl_state()
        log("A", "gfn-monitor.py:tick", "awdl sample", {"n": n, **a})
        if n == 1 or n % 15 == 0:
            log("A", "gfn-monitor.py:wifi", "wifi sample", {"n": n, **wifi_state()})
        ping = ping_sample(args.ping_host)
        log("B", "gfn-monitor.py:ping", "ping sample", {"n": n, **ping})
        if n == 1 or n % 5 == 0:
            log("E", "gfn-monitor.py:gfnlog", "gfn log signals", {"n": n, **gfn_log_signals()})
            log("E", "gfn-monitor.py:udp", "gfn udp sockets", {"n": n, **netstat_udp_gfn()})
            log("D", "gfn-monitor.py:load", "process / gfn running", {
                "n": n,
                "gfn_running": gfn_running(),
                "top_net": sh("ps -axo %cpu=,command= | sort -nr | head -8").strip()[:500],
            })
        if ping.get("loss_pct") and ping["loss_pct"] > 0:
            log("B", "gfn-monitor.py:loss", "ICMP loss detected", {"n": n, **ping})
        if ping.get("rtt_dev_ms") and ping["rtt_dev_ms"] > 15:
            log("B", "gfn-monitor.py:jitter", "high ICMP jitter", {"n": n, **ping})
        if a.get("awdl_up"):
            log("A", "gfn-monitor.py:awdl_active", "awdl still up during session", {"n": n})
        time.sleep(args.interval)

    log("C", "gfn-monitor.py:end", "monitor end", {"ticks": n, "profile": gfn_profile()})
    print(json.dumps({"ok": True, "ticks": n, "out": str(args.out)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
