# GitHub / open tools: AWDL control for Mac Wi‑Fi latency (cloud gaming)

**Context:** Apple Wireless Direct Link (AWDL) uses the `awdl0` interface. On Wi‑Fi, AWDL activity can correlate with latency spikes/jitter. Pure `sudo ifconfig awdl0 down` is often insufficient on modern macOS because the system brings the interface back up quickly; practical tools use a **privileged helper or LaunchDaemon** that reacts to kernel/interface events and keeps `awdl0` administratively down while enabled.

**Scope:** Installable CLI or macOS apps aimed at macOS 14–26 (Sonoma through Tahoe). Research date: 2025-11-06.

**Homebrew:** `brew search awdl` / `brew info --cask ping-warden` on this machine found **no core formula/cask** for `awdlkiller` or `ping-warden`. Ping Warden’s docs mention a **third-party tap** (`brew tap oliverames/tap` then `brew install --cask ping-warden`); treat as **vendor-specific** and verify before relying on it.

---

## Ranked list (best → weaker fit for GeForce NOW on Wi‑Fi *today*)

| Rank | Repository | URL | License | Install (no App Store) | Password / approval every time? | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | **Stop Stutter** | https://github.com/burakgon/stop-stutter | **MIT** | Download universal ZIP from [Releases](https://github.com/burakgon/stop-stutter/releases/latest) → move `Stop Stutter.app` to `/Applications` → open → **Enable Helper** | **No** for normal play after one-time helper approval in **System Settings → General → Login Items & Extensions** (admin/Touch ID once per doc) | Native SwiftUI; **presets include GeForce NOW** and other streamers; keeps `awdl0` down via helper while “Boost” is on. Explicitly targets the stutter/jitter use case. |
| 2 | **AWDLControl** | https://github.com/james-howard/AWDLControl | **MIT** | [Releases](https://github.com/james-howard/AWDLControl/releases) → download signed build → drag `AWDLControl.app` to Applications → launch → **Register Helper** | **No** after one-time **Register Helper** (admin for SMAppService helper); UI/menu bar must be running for helper behavior described in README | Game-aware modes (**Game Mode** disables AWDL when a game is frontmost). Free. Not App Store; GitHub-only releases (e.g. v1.0.6). Good general-purpose choice if you want game detection vs always-on. |
| 3 | **awdlkiller** | https://github.com/jamestut/awdlkiller | **Not declared** (no `LICENSE` in repo; treat as “all rights reserved” until clarified) | `make awdlkiller` then `sudo python3 misc/installer.py` (installs binary, LaunchDaemon plist, `awdl` manager to `/usr/local/bin`). Prebuilt **v1** asset on Releases for universal binary. | **Install** needs `sudo` once. Day-to-day: daemon runs as root; `awdl off` / `awdl on` / `awdl status` per README — **may require `sudo`** for control if `/usr/local/bin/awdl` is root-only (verify permissions after install). | CLI-oriented; proven approach (AF_ROUTE / ioctl) cited by other projects. Open issues report “doesn’t work” on some setups — test on your Mac. |
| 4 | **Ping Warden** | https://github.com/oliverames/ping-warden | **MIT** (source) | **Prebuilt:** [Releases](https://github.com/oliverames/ping-warden/releases) / product site; **from source:** clone repo, open Xcode project, sign all targets, install to `/Applications` | **No** recurring GUI password after initial **Login Items & Extensions** approval; **prebuilt “Ping Protection” is paid** (see below) | **Open source ≠ gratis binary:** README states prebuilt app needs a **one-time ~$15 license** to enable Ping Protection / protected sessions; source remains MIT for build/audit. Dashboard/network metrics beyond basic AWDL toggle. macOS 26: Control Center toggle. |
| 5 | **AWDL Controller (Raycast)** | https://github.com/OnCloud125252/AWDL-Controller | **Not declared** in API | Requires **Raycast**; extension installs helper via **Install Helper** (downloads release, checksum) | **One-time** admin for helper install; README claims **no password after that** | Nice if you already live in Raycast: root helper + optional “watched apps” agent. More moving parts than a single-purpose app. |
| 6 | **awdl_wifi_scripts** | https://github.com/meterup/awdl_wifi_scripts | **MIT** | One-off: `bash <(curl -sL https://www.meter.com/awdl.sh)` **or** daemon: `curl -sL https://www.meter.com/awdl-daemon.sh \| bash` (see repo README) | **Yes** for interactive one-shot (types admin password). Daemon install still privileged at setup | Vendor-hosted curl scripts; reversible via GitHub `cleanup-and-reenable-awdl.sh`. Prefer if you want minimal local repo footprint and accept remote bootstrap. |
| 7 | **awdl-control** (supertowrs) | https://github.com/supertowrs/awdl-control | **Unclear** (README states upstream lacks license and describes “private” lineage — verify before fork/redistribute) | `make awdlkiller` then `sudo ./system/install.sh`; then `sudo awdlctl enable` / `sudo awdlctl disable` / `awdlctl status` | **Enable/disable** commands are **`sudo`** per README | Packaging/wrapper around awdlkiller-style daemon with reversible `awdlctl` and uninstaller. Lower rank due to license ambiguity vs alternatives. |

---

## Focused evaluation (requested items)

### james-howard / AWDLControl

- **Releases:** https://github.com/james-howard/AWDLControl/releases — downloadable app bundle (not Mac App Store).
- **Install without App Store:** Download latest `.dmg`/archive from GitHub Releases → copy to `/Applications` → run → **Register Helper** (one-time elevated registration via SMAppService).
- **Works without typing password every session:** Yes, after helper registration; ongoing control is via the app/menu bar (quit restores AWDL per README).
- **macOS:** README requires **macOS 13+**; suitable for 14–26.

### jamestut / awdlkiller (and similar CLIs)

- **Role:** Root-capable daemon + optional `awdl` manager script; puts `awdl0` down immediately when the kernel brings it up.
- **Install:** Build + `sudo python3 misc/installer.py`, or manual plist + LaunchDaemon steps in README.
- **License:** No `LICENSE` file detected via GitHub API — **not clearly open license**; use only if you accept that risk or obtain author clarification.

### oliverames / ping-warden — open vs paid

- **Source:** **MIT** on GitHub; you can build and modify under MIT.
- **Prebuilt binary / “Ping Protection”:** README and product docs describe a **paid license** to unlock full protection flows on distributed builds; treat **GitHub Releases binary as commercial feature-gated** unless you verify current pricing/terms on https://pingwarden.app .
- **Helper behavior:** Privileged helper + one-time System Settings approval; not designed to prompt every launch.

### Brew formulas / raw scripts + privileged helper

- **Core Homebrew:** No widely indexed `awdl*` formula/cask in default taps (verified locally 2025-11-06).
- **Third-party tap:** Ping Warden docs reference `brew tap oliverames/tap` — **not verified** here; run `brew tap` / `brew info` yourself before scripting.
- **meterup/awdl_wifi_scripts:** MIT repo wrapping **curl | bash** installers that install a persistent helper/daemon (admin at install).

---

## Recommendation: GeForce NOW on Mac Wi‑Fi **right now**

1. **Fastest path with GFN in the name:** Use **[burakgon/stop-stutter](https://github.com/burakgon/stop-stutter)** — it lists GeForce NOW as a first-class preset, uses a signed/notarized app from Releases, MIT-licensed, and automates AWDL suppression only while streaming (or “Always on” if you prefer). One-time helper approval, then play.

2. **Free alternative without streamer-specific UI:** Use **[james-howard/AWDLControl](https://github.com/james-howard/AWDLControl)** from GitHub Releases — enable **Game Mode** (or **AWDL Off** if the GFN app isn’t detected as a game) after registering the helper.

3. **CLI / minimal GUI:** **[jamestut/awdlkiller](https://github.com/jamestut/awdlkiller)** if you are comfortable with LaunchDaemons and possible `sudo` for toggles — confirm license with the author if redistribution or workplace policy matters.

4. **Ping Warden:** Strong feature set and MIT source, but **budget for the license** if you use official binaries, or **build from source** in Xcode if you want zero cost and accept signing/setup effort.

**Operational note:** While AWDL is suppressed, AirDrop, AirPlay-to-device, Handoff, Sidecar, Universal Control, and similar features that rely on AWDL may fail — turn suppression off when you need them.

---

## Sources

- GitHub: repository READMEs and release pages for projects listed above  
- `gh search repos awdl`, `gh repo view` (license metadata where available)  
- Local: `brew search` / `brew info --cask ping-warden` (no default cask hit)

---

*This document is research notes, not legal advice on licenses. Confirm license and security posture before installing anything with root access.*
