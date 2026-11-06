# GFN Mac connectivity playbook

Derived from local research (Nov 2026). Full narrative: `~/reports/GFN Mac connectivity fixes.md` if present.

## Session Report triage

| Lowest score | Meaning | Action |
|---|---|---|
| Packets Delivery | Drops / Wi‑Fi / congestion | AWDL off, Ethernet A/B, lower bitrate |
| Download | Lag / buffering on stream path | Bufferbloat / bitrate / QoS |
| Upload | Input path loss/jitter | Uplink contention, AWDL |
| Device | Local decode / CPU | Quit apps, lower res |
| Game | Remote COD FPS before encode | In-game settings (not Mac AWDL) |

## Ordered steps

1. VPN off → GFN Network Test → play → Session Report  
2. Classify by lowest score  
3. Ethernet A/B on the same router  
4. Mac Wi‑Fi: AWDL suppress, Location Services off, EU prefer ch **44 @ 80 MHz**  
5. Apply `gfn-patch-settings.py apply --preset stable`  
6. Remeasure with `gfn-monitor.py`  

## Do not

- Binary-patch `GeForceNOW.app` (breaks signing / Gatekeeper; does not fix Wi‑Fi)  
- Raise bitrate to “fix” bufferbloat  
- Trust Speedtest Mbps alone  
