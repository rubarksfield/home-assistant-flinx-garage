"""Keep verification entirely offline, including accidental transport calls."""

import socket

import pytest

from custom_components.flinx_garage import coordinator


@pytest.fixture(autouse=True)
def no_live_transports(monkeypatch):
    def denied(*args, **kwargs):
        pytest.fail("Tests must not connect to a live network or opener")

    async def denied_ble(*args, **kwargs):
        denied()

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(socket, "getaddrinfo", denied)
    monkeypatch.setattr(coordinator, "establish_connection", denied_ble)
