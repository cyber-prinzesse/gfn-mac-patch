# gfn-mac-patch

macOS helpers to **measure** and **safely tune** GeForce NOW connectivity (packet loss / hitching / mouse lag) without binary-patching `GeForceNOW.app`.

Based on the research in [docs/playbook.md](docs/playbook.md): high Mbps ≠ smooth stream; AWDL, bufferbloat, and aggressive stream settings (HDR / uncapped bitrate) are the usual culprits on Mac Wi‑Fi.

## What this is / isn’t

| Does | Does not |
|---|---|
| Monitor AWDL, Wi‑Fi, ICMP loss/jitter, GFN log signals | Patch or crack `GeForceNOW.app` |
| Back up and adjust **GFN preference JSON** (HDR, bitrate, profile) | Bypass NVIDIA ToS or anti-cheat |
| Point you at AWDL Control / Session Report | Promise ISP-level fixes |

## Quick start

```bash
cd ~/Developer/gfn-mac-patch
chmod +x bin/*

# 1) Measure while you play (~15 min)
./bin/gfn-monitor.py --duration 900 --out ~/.cursor/gfn-session.ndjson

# 2) Apply the safe settings patch (backs up first)
./bin/gfn-patch-settings.py apply --preset stable

# 3) Restore previous prefs if needed
./bin/gfn-patch-settings.py restore
```

After a COD session: GeForce NOW → **Help → Session report**. Compare **Packets Delivery** vs **Game**.

## Tools

| Script | Role |
|---|---|
| `bin/gfn-monitor.py` | NDJSON session monitor (hypotheses A–E) |
| `bin/gfn-patch-settings.py` | Safe `sharedstorage.json` preset (stable / restore) |
| `bin/gfn-awdl-status.sh` | Show whether `awdl0` is up (AirDrop radio) |

For persistent AWDL suppression use [AWDL Control](https://github.com/james-howard/AWDLControl) or [Ping Warden](https://pingwarden.app/) — a one-shot `ifconfig awdl0 down` does not stick on modern macOS.

## Preset `stable`

Writes into GeForce NOW `sharedstorage.json` (with timestamped backup):

- HDR streaming **off**
- Cap max bitrate (**35 Mbps**, auto off)
- Prefer **balanced** streaming profile
- Keep Reflex **on**, fps **60**, packet size **1432**

Quit and relaunch GeForce NOW after applying.

## License

MIT — see [LICENSE](LICENSE).
