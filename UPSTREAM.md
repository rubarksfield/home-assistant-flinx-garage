# Source and attribution

This community fork derives from [b12e/flinx-garage-ha](https://github.com/b12e/flinx-garage-ha), by Bram Vandeperre, under the MIT license.

The starting source is stable **v3.1.0**, commit `e317a0ae332ec190543c6bab7afd0a2e277c6964`. The original copyright and permission notice remain in [LICENSE](LICENSE). Upstream brand assets are retained.

This repository begins with a reviewed source snapshot. Upstream Git history was not imported because a historical verification fixture describes data from a real door log and key. That history is not needed to install the integration.

Fork v3.1.1 adds consistent naming, installation and troubleshooting docs, safe support forms, reproducible checks and narrower logging. Door control, transport selection, account configuration format and entity identifiers remain based on upstream v3.1.0.

The shared vendor MQTT app credential is a public protocol constant inherited from upstream, separate from a user's account password and per-device key. It remains for compatibility and has a narrowly scoped scanner exception. See [privacy notes](docs/security.md).

Review future upstream updates as source diffs and repeat the privacy checks. Do not import historical packet logs or real-device fixtures.
