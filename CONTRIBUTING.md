# Contributing

Small, clear contributions are welcome. Check existing issues before starting a larger change and preserve the original MIT attribution.

## Develop and verify

Install [uv](https://docs.astral.sh/uv/), then run:

```sh
uv sync --frozen
uv run --frozen pytest -q
uv run --frozen ruff check .
git diff --check
```

Development uses Python 3.14.2 and Home Assistant 2026.9.2. Tests use fabricated data and offline transports. They must never connect to a real opener, account, MQTT broker or Bluetooth peripheral.

Add a regression test before changing control, parsing or privacy behavior. Record user-facing changes under Unreleased in CHANGELOG.md. Keep the `flinx_garage` domain and entity unique IDs stable unless a tested migration accompanies a change.

## Before publishing

Review the complete staged diff. With Gitleaks 8.30.1 installed, run:

```sh
gitleaks git . --staged --redact=100 --ignore-gitleaks-allow
gitleaks git . --log-opts="--all" --redact=100 --ignore-gitleaks-allow
git diff --cached --check
```

Also scan a clean export with `gitleaks dir`; include image metadata, examples, CI output and release notes in the review. The only credential exception is the exact public vendor MQTT constant at its assignment. Do not widen it to an entire file or directory.

## Safe reports

Use the issue forms. Include versions, connection mode, the symptom and a short reviewed excerpt. Remove account details, tokens, device keys/IDs, opener names, MAC/IP addresses and household names. Do not upload raw captures, Home Assistant `.storage`, or full dashboard/configuration dumps.

Security concerns belong in the private vulnerability-reporting channel; see SECURITY.md.
