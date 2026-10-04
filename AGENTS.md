# Garage integration operating rules

- Keep the flinx_garage domain, configuration format and entity unique IDs stable.
- Preserve upstream MIT copyright, license and source attribution.
- Update CHANGELOG.md for material changes and release a new stable version for runtime changes.
- Never commit account credentials, device keys, personal identifiers, household configuration, captures or unreviewed diagnostics.
- Use fabricated data and offline transports in tests; never operate a real door.
- Keep private evidence outside this repository. Review examples and image metadata.
- Before publication run the full offline suite, Ruff, staged diff checks and Gitleaks 8.30.1 for source, staged files and all history. Review the final diff and CI output.
- Do not broaden the exact vendor protocol-constant exception in .gitleaks.toml.
- Use a verified GitHub noreply commit address. Do not import upstream history containing real-device fixtures.
