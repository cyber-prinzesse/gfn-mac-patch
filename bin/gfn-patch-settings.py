#!/usr/bin/env python3
"""Safe GeForce NOW preference patch (sharedstorage.json) — not a binary patch.

Presets adjust streaming aggressiveness for Mac Wi-Fi / bufferbloat.
Always writes a timestamped backup next to the file before changing anything.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

GFN = Path.home() / "Library/Application Support/NVIDIA/GeForceNOW"
STORAGE = GFN / "sharedstorage.json"
BACKUP_DIR = GFN / "gfn-mac-patch-backups"

PRESETS = {
    "stable": {
        "description": "HDR off, bitrate capped at 35 Mbps, balanced profile — stability over peak quality",
        "streamingProfiles": "balanced",
        "custom": {
            "hdrStreaming": False,
            "maxBitrateAuto": False,
            "maxBitrate": 35000,
            "fps": 60,
            "reflex": True,
            "maxPacketSize": 1432,
            "bitDepth": 8,
        },
    },
    "competitive": {
        "description": "Like stable but slightly higher cap (45 Mbps) for 1080p60 headroom",
        "streamingProfiles": "balanced",
        "custom": {
            "hdrStreaming": False,
            "maxBitrateAuto": False,
            "maxBitrate": 45000,
            "fps": 60,
            "reflex": True,
            "maxPacketSize": 1432,
            "bitDepth": 8,
        },
    },
}


def load() -> dict:
    if not STORAGE.exists():
        raise SystemExit(f"missing {STORAGE} — launch GeForce NOW once first")
    return json.loads(STORAGE.read_text())


def backup(data: dict | None = None) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = BACKUP_DIR / f"sharedstorage-{stamp}.json"
    if data is None:
        shutil.copy2(STORAGE, dest)
    else:
        dest.write_text(json.dumps(data, indent=2) + "\n")
    return dest


def show(data: dict) -> None:
    cfg = data.get("appSettingsConfig", {})
    custom = cfg.get("customProfile", {})
    print(json.dumps(
        {
            "path": str(STORAGE),
            "streamingProfiles": cfg.get("streamingProfiles"),
            "customProfile": {
                k: custom.get(k)
                for k in (
                    "fps",
                    "hdrStreaming",
                    "maxBitrate",
                    "maxBitrateAuto",
                    "maxPacketSize",
                    "reflex",
                    "bitDepth",
                    "primaryDisplayResolution",
                )
            },
        },
        indent=2,
    ))


def apply_preset(name: str) -> None:
    if name not in PRESETS:
        raise SystemExit(f"unknown preset {name!r}; choose: {', '.join(PRESETS)}")
    preset = PRESETS[name]
    data = load()
    bak = backup()
    cfg = data.setdefault("appSettingsConfig", {})
    cfg["streamingProfiles"] = preset["streamingProfiles"]
    custom = cfg.setdefault("customProfile", {})
    custom.update(preset["custom"])
    # Ensure custom profile is selected when present
    shared = custom.setdefault("sharedSettings", {})
    shared["streamingProfiles"] = "custom"
    STORAGE.write_text(json.dumps(data, indent=2) + "\n")
    print(f"applied preset={name}")
    print(f"backup={bak}")
    print(preset["description"])
    print("Quit and relaunch GeForce NOW for settings to take effect.")
    show(load())


def restore_latest() -> None:
    if not BACKUP_DIR.is_dir():
        raise SystemExit("no backups found")
    backups = sorted(BACKUP_DIR.glob("sharedstorage-*.json"))
    if not backups:
        raise SystemExit("no backups found")
    src = backups[-1]
    # backup current before overwrite
    backup()
    shutil.copy2(src, STORAGE)
    print(f"restored from {src}")
    show(load())


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show", help="print current streaming-related prefs")
    ap = sub.add_parser("apply", help="apply a preset (backs up first)")
    ap.add_argument("--preset", default="stable", choices=sorted(PRESETS))
    sub.add_parser("restore", help="restore newest backup")
    sub.add_parser("list-presets", help="list presets")
    args = p.parse_args()

    if args.cmd == "list-presets":
        for k, v in PRESETS.items():
            print(f"{k}: {v['description']}")
        return 0
    if args.cmd == "show":
        show(load())
        return 0
    if args.cmd == "apply":
        apply_preset(args.preset)
        return 0
    if args.cmd == "restore":
        restore_latest()
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
