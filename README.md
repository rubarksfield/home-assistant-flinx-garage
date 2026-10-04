# 🚪 F-LINX Garage Door for Home Assistant

**Open sesame. Welcome home.**

Give your F-LINX garage door a place in Home Assistant: open, close and stop it, switch its light, follow its position and keep track of operating cycles.

![F-LINX garage door illustration](docs/images/garage-hero.svg)

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5?logo=homeassistant&logoColor=white)](https://www.hacs.xyz/docs/faq/custom_repositories/)
[![Release](https://img.shields.io/github/v/release/rubarksfield/home-assistant-flinx-garage)](https://github.com/rubarksfield/home-assistant-flinx-garage/releases)
[![HACS and hassfest](https://github.com/rubarksfield/home-assistant-flinx-garage/actions/workflows/validate.yml/badge.svg)](https://github.com/rubarksfield/home-assistant-flinx-garage/actions/workflows/validate.yml)
[![Tests](https://github.com/rubarksfield/home-assistant-flinx-garage/actions/workflows/tests.yml/badge.svg)](https://github.com/rubarksfield/home-assistant-flinx-garage/actions/workflows/tests.yml)
[![Secret scan](https://github.com/rubarksfield/home-assistant-flinx-garage/actions/workflows/secrets.yml/badge.svg)](https://github.com/rubarksfield/home-assistant-flinx-garage/actions/workflows/secrets.yml)
[![MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

This is a community fork of [Bram Vandeperre's F-LINX integration](https://github.com/b12e/flinx-garage-ha), based on upstream v3.1.0. The original MIT license and author credit are preserved. It is independent of F-LINX, Force-Door and Move Automation.

## What you get

| Entity | What it does |
| --- | --- |
| Garage door cover | Open, close, stop and follow reported position |
| Opener light | Switch the opener's built-in light |
| Operation counter | Track the controller's cumulative operating cycles |

One integration entry manages one F-LINX account and its selected doors. Add or remove doors later under **Configure → Manage devices**.

## Is my opener supported?

Your opener must already work in the **F-LINX app** and be online. A compatible F-LINX Wi-Fi module or USB dongle provides the connection. The motor's brand or an Espressif Wi-Fi chip alone does not establish compatibility.

A Move Automation FORCE with an F-LINX module has been used with upstream v3.1.0 in **Cloud only** mode on Home Assistant 2026.9.2. Other opener and firmware combinations need their own verification. The upstream minimum is Home Assistant **2025.2.0**; this fork's automated checks use **2026.9.2**.

For cloud commands, you need your F-LINX account and an internet connection. For Bluetooth commands, you also need an adapter or an **active ESPHome Bluetooth proxy** within range. A passive scanner cannot send commands. An opener's LAN IP is not a configuration field; this integration uses the vendor cloud and/or Bluetooth.

## Install with HACS

[![Add to HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=rubarksfield&repository=home-assistant-flinx-garage&category=integration)

1. Click **Add to HACS**, or open **HACS → ⋮ → Custom repositories** and add `https://github.com/rubarksfield/home-assistant-flinx-garage` as **Integration**.
2. Find **F-LINX Garage Door**, download the latest stable release and restart Home Assistant.
3. Open **Settings → Devices & services → Add integration → F-LINX Garage Door**.
4. Sign in with your F-LINX account and select the doors you want. The picker initially selects all doors, so review the selection.
5. Choose a connection mode under **Configure → Connection mode**. **Cloud only** works without Bluetooth hardware.

This is a **HACS custom repository**. Default-list inclusion is a separate review; passing validation does not mean it has been accepted into the default catalog.

### Already using the upstream integration?

This fork keeps the `flinx_garage` domain, configuration format and entity unique IDs. Choose one repository to manage that domain; installing both makes HACS ownership and updates ambiguous. Back up Home Assistant before switching sources, preserve the existing integration entry, and verify that the same doors and entities return after a restart. Do not delete and recreate your account entry just to change the repository URL.

### Manual install

Download a [stable release](https://github.com/rubarksfield/home-assistant-flinx-garage/releases), then copy `custom_components/flinx_garage/` into `config/custom_components/flinx_garage/`. Restart Home Assistant and follow the account setup above.

## Choose how it connects

| Mode | Commands | State updates |
| --- | --- | --- |
| **Bluetooth only** | Bluetooth | Replies to commands sent by Home Assistant |
| **Bluetooth preferred, cloud fallback** (upstream default) | Bluetooth first, then cloud | MQTT push, cloud polling and Bluetooth replies |
| **Cloud preferred, Bluetooth fallback** | Cloud first, then Bluetooth | MQTT push, cloud polling and Bluetooth replies |
| **Cloud only** | Cloud; Bluetooth is disabled | MQTT push and cloud polling |

**Bluetooth only** avoids cloud traffic after initial account setup. Its position can become stale when someone uses a remote, wall button, app or auto-close timer. After a Home Assistant restart, position is unknown until a command reply arrives. Choose a cloud-enabled mode if those outside changes need to appear in Home Assistant.

With several doors, the integration uses the opener identity reported by the account. Without an identity it will not guess between multiple doors. With one configured door, the upstream Bluetooth behavior can use any matching `Noru_*` or `opener_*` device in range.

### Partial opening

Intermediate percentages use software timing: the integration starts movement and sends stop near the requested position. Results are approximate, especially with cloud latency. `0%` and `100%` use the ordinary close/open commands. Partial opening has not been physically verified for the Move Automation FORCE installation.

## Give it a dashboard home

Add a **Tile card** for your garage door cover, then enable **Cover open/close**. Add tiles for the opener light and operation counter. These are built-in Home Assistant cards; no extra dashboard plugin is needed.

Use the entities listed under your device. See [the reusable dashboard example](examples/dashboard.yaml); replace its placeholder entities before use.

## If the door is feeling stubborn

| Symptom | Check |
| --- | --- |
| No doors after sign-in | Confirm the same account sees its doors in the F-LINX app. |
| Bluetooth unavailable | Check range and an active proxy's free connection slot, or choose Cloud only. |
| State changes arrive slowly | Cloud state can lag; optional periodic polling is under Configure. Avoid repeated button presses. |
| App and Home Assistant lose their session | The vendor API allows one active session per account. Reopening the app can invalidate Home Assistant's session; it will sign in again when needed. |
| Unavailable after an update | Check release notes and integration logs before reinstalling. |

For help, [open a bug report](https://github.com/rubarksfield/home-assistant-flinx-garage/issues/new?template=bug_report.yml) with a short, reviewed excerpt. Keep passwords, account emails, device keys, door IDs, Bluetooth names/addresses and captures private.

## Privacy and contributing

Credentials and device keys stay in Home Assistant's configuration entry. This repository contains no household configuration or packet captures. The fork removes identifying response, frame, topic and Bluetooth details from its own logs. Home Assistant and third-party libraries may still write sensitive diagnostics, so review logs before sharing them.

The vendor MQTT connection uses port 1883 without TLS and a shared app credential already present in upstream public source. Payload encryption does not make the entire connection private. See [security and privacy](docs/security.md) for the limits and publication checks.

Contributions are welcome: clearer docs, compatibility reports with identifiers removed, and small tested fixes all help. Start with [CONTRIBUTING.md](CONTRIBUTING.md). Source provenance is recorded in [UPSTREAM.md](UPSTREAM.md).
