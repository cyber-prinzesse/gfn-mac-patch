# GeForce NOW on macOS — open tools & references

**Purpose:** Ranked, actionable projects and workflows for **network quality**, **bitrate limits**, **packet loss / jitter visibility**, and **Mac cloud-gaming stutter mitigation**. Legitimate tooling only — **no cracked clients or game cheats**.

**Ranking criteria:** (1) direct usefulness on macOS today, (2) maintenance/docs clarity, (3) alignment with NVIDIA-documented behavior (ports, overlays), (4) verifiably open source where claimed.

---

## Tier 1 — Use first on macOS

### 1. [swicken/gfn-awdl-watcher](https://github.com/swicken/gfn-awdl-watcher)

**Why:** Targets a **documented** cause of Wi‑Fi stutter on Mac: **AWDL** (Apple Wireless Direct Link) channel hops while GFN runs. Automates disable/restore around the GFN lifecycle.

**Install (quick):**

```bash
curl -sL https://raw.githubusercontent.com/swicken/gfn-awdl-watcher/main/quick-install.sh | bash
```

**Notes:** Prompts for admin once (needed to toggle `awdl0`). Re-read the repo README for uninstall and behavior before running.

---

### 2. [seifip/kilobat-cli](https://github.com/seifip/kilobat-cli) (+ optional Kilobat app)

**Why:** Open-source **macOS network diagnostics CLI** (GPL-3.0). Docs describe **`kilobat cloud-gaming`** for live/reported **ping, jitter, loss, bitrate**, and correlating stutters with Wi‑Fi band, background apps, etc. Fits **Mac cloud-gaming stutter** debugging without touching game binaries.

**Install (Homebrew):**

```bash
brew install seifip/kilobat/kilobat
kilobat --version
kilobat doctor
# During/after a session:
kilobat cloud-gaming status
kilobat cloud-gaming reports
```

**Docs:** [Kilobat CLI](https://kilobat.app/docs/cli), [cloud gaming](https://kilobat.app/cloud-gaming), [GeForce NOW on Mac](https://kilobat.app/geforce-now-mac)

---

### 3. Built-in GFN overlays & session report (not GitHub, but essential)

**In-session stats (native app):** **⌥⌘F6** (Option + Command + F6) — shows **packet loss (`pl`)**, RTT, bitrate utilization, decode timings, etc.  
**After session:** **Help → Session report** — scored breakdown including packet delivery.  
**References:** [Cloud Gaming Battle — monitor performance](https://www.cloudgamingbattle.com/monitor-performance-on-geforce-now/), [NVIDIA — Session Diagnostic Tool](https://nvidia.custhelp.com/app/answers/detail/a_id/5478), [NVIDIA — reduce lag / ports](https://nvidia.custhelp.com/app/answers/detail/a_id/4504)

These are the baseline before adding third-party tools.

---

## Tier 2 — Measurement & research code

### 4. [Hanchenli/GFN_Measurement](https://github.com/Hanchenli/GFN_Measurement)

**Why:** Collects **GFN in Chrome** stats via DevTools script → **`trace.csv`** + notebooks for analysis. Good for **bitrate / timing traces** in the **browser** path (not identical to native-app UDP ports).

**Install:**

```bash
git clone https://github.com/Hanchenli/GFN_Measurement.git
cd GFN_Measurement
# Follow README: open play.geforcenow.com, DevTools console, paste JS, export to trace.csv
```

---

### 5. [decafCG/decaf](https://github.com/decafCG/decaf) (DECAF)

**Why:** Research tool (**SIGMETRICS 2022**) automating measurement across **GeForce NOW** (and others). Useful for **repeatable benchmarking**, not day-to-day stutter fixes. Linux-oriented workflow in paper/repo.

**Install:** Clone and follow repo instructions; expect **manual game/platform setup**.

```bash
git clone https://github.com/decafCG/decaf.git
cd decaf
# See README and paper for prerequisites
```

---

## Tier 3 — Alternative open clients (GFN account; not “Mac patch” tools)

### 6. [OpenCloudGaming/OpenNOW-Mac](https://github.com/OpenCloudGaming/OpenNOW-Mac)

**Why:** Native **SwiftUI** GFN client for **Apple Silicon** — catalog, streaming, **diagnostics** paths in README. Useful if you want **open client + built-in diagnostic UX** vs stock app.

**Install (build):**

```bash
git clone https://github.com/OpenCloudGaming/OpenNOW-Mac.git
cd OpenNOW-Mac
xcodebuild build -project OpenNOW.xcodeproj -scheme OpenNOW -configuration Debug \
  -destination 'platform=macOS' CODE_SIGNING_ALLOWED=NO
```

**Also:** [OpenCloudGaming/OpenNOW](https://github.com/OpenCloudGaming/OpenNOW) publishes **Qt** `.dmg` releases for macOS ARM64 (separate from OpenNOW-Mac).

---

### 7. [verdjs/Cirrus](https://github.com/verdjs/Cirrus) / [TheRealTechCove/Cirrus](https://github.com/TheRealTechCove/Cirrus) (fork landscape)

**Why:** Unified **tvOS** client merging GFN + xCloud; README lists **live stats** (bitrate, resolution, FPS, RTT, **packet loss**). **Not a macOS app** — **Xcode + Apple TV** sideload. Listed because you asked for “Cirrus” explicitly.

**Install:**

```bash
git clone https://github.com/verdjs/Cirrus.git
cd Cirrus
cp Local.xcconfig.example Local.xcconfig
# Edit Local.xcconfig with your Apple Developer Team ID
open CloudNow.xcodeproj
# Build for Apple TV (Xcode 16+)
```

---

### 8. [owenselles/CloudNow](https://github.com/owenselles/CloudNow)

**Why:** **Apple TV / visionOS** native GFN integration with documented **max bitrate**, **L4S**, codec selection, etc. Same category as Cirrus (living room, not Mac desktop).

**Install:** See repo (TestFlight / source / IPA); **not** macOS primary.

---

## QoS / SQM — scripts & configs (router-side; helps GFN on Mac)

NVIDIA lists **native app** fixed ports **49003–49006** (UDP/TCP mix) for QoS/firewall hints:  
https://nvidia.custhelp.com/app/answers/detail/a_id/5482  

### 9. [openwrt/qosify](https://github.com/openwrt/qosify) + community GFN port marking

**Why:** **CAKE**-based QoS on **OpenWrt**. Community gist shows **`/etc/qosify/05-geforcenow.conf`** marking **udp:49003–49006** into a higher tier so bulk traffic does not starve UDP game media.

**Reference gist (OpenWrt steps, not a standalone repo):**  
https://gist.github.com/GetVladimir/2ff48f4729884148f0567bb63ffd8b43  

**Pattern (on router after qosify install):**

```bash
# On OpenWrt — illustration only; adjust WAN speeds and paths per your build
cat >> /etc/qosify/05-geforcenow.conf <<'EOF'
# GeForce NOW (client-side ports — verify against NVIDIA docs for your client)
udp:49003 +video
udp:49004 +video
udp:49005 +video
udp:49006 +video
EOF
/etc/init.d/qosify restart
```

---

### 10. [sqm-autorate/sqm-autorate](https://github.com/sqm-autorate/sqm-autorate)

**Why:** Dynamically adjusts **CAKE SQM** rates on variable links (DOCSIS/LTE). Indirectly helps **stable latency** for UDP streaming under load.

**Install:** Follow OpenWrt wiki + repo; applies to **router**, not Mac.

---

### 11. [Segalmen/openwrt-custom](https://github.com/Segalmen/openwrt-custom)

**Why:** **DSCP + CAKE** custom SQM scripts and nftables classification for **gaming prioritization** on OpenWrt. Add **49003–49006** to priority port lists if you use this stack (repo documents extending port lists).

---

## `sharedstorage.json` — safe edits (macOS)

**Path (typical):**  
`~/Library/Application Support/NVIDIA/GeForceNOW/sharedstorage.json`

**Safe workflow (manual — no well-known dedicated GitHub “safe editor” found in search):**

1. **Quit GFN completely** — ensure no `GeForceNOW` processes remain (Activity Monitor).
2. **Copy** the file: `cp sharedstorage.json sharedstorage.json.bak.$(date +%Y%m%d)`.
3. Edit **one logical block** at a time (e.g. resolution / `maxBitrateValue` for your target preset). **Valid JSON** only.
4. Save, relaunch GFN. If the UI overwrites values, community reports vary by version — treat as **unsupported** by NVIDIA.
5. **Do not** mark read-only blindly; it can break updates. Prefer backups + revert.

**Related (Linux Flatpak, not macOS `sharedstorage.json`):** HiDPI gist edits **`storage.json` / CEF prefs** for Linux Flatpak — pattern for “kill app → backup → edit JSON” only:  
https://gist.github.com/holdenger/d2133da17cb2793569b5640204573da8  

---

## Logging / stats for UDP **49003–49006** on macOS

**Reality check:** NVIDIA documents these ports for the **native** client. **Browser** streaming uses different paths. There is **no** widely cited open-source tool that solely exports **GFN’s internal** loss metric from those sockets; combine **GFN overlay** + **packet capture** for ground truth.

### A. Quick capture (read-only)

**Requires:** GFN native app running a session; wired capture preferred.

```bash
# List interfaces first
ifconfig

# Capture all GFN-documented client ports (adjust en0 vs your active interface)
sudo tcpdump -i en0 -w ~/Desktop/gfn-ports.pcap 'udp portrange 49003-49006 or tcp port 49006'

# Live summary (packet counts per second by port)
sudo tcpdump -i en0 -nn 'udp portrange 49003-49006 or tcp port 49006'
```

Open **`gfn-ports.pcap`** in **Wireshark** (macOS): filter `udp.port >= 49003 && udp.port <= 49006` (and TCP 49006 if seen).

### B. Research alignment

Academic/traffic analysis papers describe **RTP**-like flows on **49003–49006** and high volume on **49005** video — useful when interpreting pcaps:  
- https://arxiv.org/html/2401.06366 (network anatomy, GFN)  
- https://arxiv.org/html/2012.06774v2 (Stadia/GFN/PSNow analysis)

---

## Other Mac-adjacent repos (review before use)

| Repo | Role |
|------|------|
| [ComicBit/Geforce-Now-Mac-stutter-free-Launcher](https://github.com/ComicBit/Geforce-Now-Mac-stutter-free-Launcher) | AWDL toggle via LaunchAgent — **overlap** with `gfn-awdl-watcher`; compare approaches |
| [JohnDeved/geforce-now-hdr-mac](https://github.com/JohnDeved/geforce-now-hdr-mac) | **HDR display** patch via copy in `~/Applications` — quality/visual, not network |
| [googleman81/Shadow-bash-script](https://github.com/googleman81/Shadow-bash-script) | README positioning unclear vs **Shadow PC** vs GFN — **audit before running** |

---

## Explicitly excluded

- **Cracked / modified official clients**, credential theft, or **in-game cheats** — not listed.
- **[Ixve/gfn-queue-checker](https://github.com/Ixve/gfn-queue-checker)** — archived queue scraper; **out of scope** for network quality tooling here.

---

## Summary table

| Priority | Item | macOS | Focus |
|----------|------|-------|--------|
| 1 | gfn-awdl-watcher | Yes | Wi‑Fi / AWDL stutter |
| 2 | kilobat-cli | Yes | Loss/jitter/bitrate session forensics |
| 3 | GFN ⌥⌘F6 + Session report | Yes | Official stats |
| 4 | GFN_Measurement | Yes (browser) | Trace export / analysis |
| 5 | OpenNOW-Mac | Yes (build) | Open native client + diagnostics |
| 6 | qosify + GFN port rules | Router | QoS for 49003–49006 |
| 7 | tcpdump + Wireshark | Yes | UDP port logging / proof |

---

*Generated for local reference — verify repo licenses and READMEs before use. NVIDIA trademarks belong to NVIDIA.*
