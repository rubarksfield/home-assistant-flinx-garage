# Security and privacy notes

## What stays in Home Assistant

The integration stores the account username/password and device keys in Home Assistant configuration entries. Backups may contain them. Do not share `.storage`, diagnostics exports or unreviewed logs publicly.

This fork logs statuses, counts and error types instead of account response bodies, private MQTT topics, raw or decrypted frames, opener names/addresses and device aliases. Unknown cloud rejection text becomes a generic error; known offline and rate-limit messages remain useful. Third-party and Home Assistant logs are outside that guarantee.

## Transport limits

Cloud account and command requests use HTTPS with normal certificate verification. MQTT state uses the upstream broker on **port 1883 without TLS**. The shared app credential is already embedded in upstream public source. Device payload encryption leaves MQTT credentials and topic metadata exposed to an observer of that connection. This fork preserves the protocol; it does not claim to repair the vendor transport.

Bluetooth-only mode avoids cloud requests after initial provisioning but has limited state visibility. It misses operations initiated by other controls. Software position control is approximate.

## Publication review

This repository starts from the reviewed upstream v3.1.0 source snapshot. Historical real-door test material was excluded, and identifying sample addresses in comments were replaced with descriptions. Tests use fabricated data only.

Publication checks cover three views:

1. Source, examples and staged files: secret scanning plus exact comparisons against privately held household identifiers and available credentials.
2. Git history and release source: scan every object being published, and review the original license and attribution.
3. GitHub metadata, release notes, issues and Actions logs: repeat the review after publication.

`.gitleaks.toml` permits only the exact shared app constant at its assignment in `const.py`; arbitrary secrets in that file are still scanned. CI uses checksum-verified Gitleaks 8.30.1 and scans all fetched history.

This is a bounded privacy review. New commits and user-submitted reports need their own checks.
