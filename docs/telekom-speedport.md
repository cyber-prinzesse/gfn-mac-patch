# Telekom Speedport Smart 4 + GeForce NOW (no Ethernet)

Your DHCP banner is `Speedport_Smart_4_Typ_A` → gateway `http://speedport.ip` / `http://192.168.2.1`.

## Why Download = 0 on Magenta DSL/VDSL

GFN **Download** scores latency-under-load on the path to NVIDIA. Speedport + Wi‑Fi often shows:

- High **Mbps** (fine)
- **Low uplink responsiveness** (bufferbloat) when anything saturates the line
- Extra Wi‑Fi hits on **DFS channel 100** and **AWDL**

Packet Delivery can still look good (yours was **94**).

## Speedport steps (do these in the router UI)

1. Open **http://speedport.ip** (device password on the router sticker).
2. **WLAN → 5 GHz channel**  
   Set to **44** (or **36/40/48**) at **80 MHz**. Avoid **100+** (DFS) for GFN.
3. **Priorisiertes WLAN** (handbook ~p.204)  
   Create the VIP SSID, connect **only this Mac** to it. Speedport then guarantees ~50% of the line to that client. Do **not** give the VIP key to phones/consoles.
4. **Do not** rely on “prioritize whole device” while that device also downloads — Speedport cannot do port-based QoS for 49003–49006.
5. Reboot the Speedport once after channel change.
6. Keep **VPN off** while playing (ProtonVPN is installed but was disconnected — leave it that way for GFN).

## Mac side (already in this repo)

```bash
./bin/gfn-patch-settings.py apply --preset bufferbloat   # 15 Mbps, HDR off
./bin/gfn-awdl-status.sh                                 # should be inactive while gaming
```

Use **AWDL Control → AWDL Off** (Register Helper once) every session.

## Verify

Play 15–20 min → GFN **Help → Session report**. Success = **Download** no longer **0** (aim ≥50) with Packet Delivery still high.
