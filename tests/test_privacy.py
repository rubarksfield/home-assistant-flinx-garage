"""Regression checks using fabricated data; no network or door commands."""

import asyncio
import logging
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import aiohttp
import pytest

from custom_components.flinx_garage import coordinator as coordinator_module
from custom_components.flinx_garage import mqtt_client as mqtt_module
from custom_components.flinx_garage.account import CannotConnect, FlinxAccount
from custom_components.flinx_garage.coordinator import FlinxGarageCoordinator

# Deliberately readable canaries, unrelated to any account or physical device.
CANARY = "fabricated-private-marker"
FAKE_KEY = bytes(range(16)).hex()


class Response:
    """Offline substitute for an aiohttp request context manager."""

    def __init__(self, payload=None, status=200, error=None):
        self.payload = payload
        self.status = status
        self.error = error

    async def __aenter__(self):
        if self.error:
            raise self.error
        return self

    async def __aexit__(self, *args):
        return False

    async def json(self):
        return self.payload


@pytest.fixture(autouse=True)
def debug_logs(caplog):
    caplog.set_level(logging.DEBUG, logger="custom_components.flinx_garage")


@pytest.mark.parametrize("operation", ["login", "query"])
@pytest.mark.parametrize(
    "payload",
    [
        {"code": 400, "msg": CANARY, "data": {"devKey": CANARY}},
        {"code": 200, "data": {"private": CANARY}},
    ],
)
async def test_account_responses_do_not_expose_payload(operation, payload, caplog):
    """Logging a rejected/missing-token response would disclose its contents."""
    account = FlinxAccount(CANARY, CANARY)
    session = SimpleNamespace(post=lambda *a, **kw: Response(payload))
    if operation == "login":
        await account.async_login(session)
    else:
        # Only rejected response shapes are meaningful on the query path.
        if payload["code"] == 200:
            payload = {"code": 400, "msg": CANARY, "data": payload["data"]}
            session = SimpleNamespace(post=lambda *a, **kw: Response(payload))
        await account.async_query_devices(session, CANARY)
    assert CANARY not in caplog.text


@pytest.mark.parametrize("operation", ["login", "query", "get_token"])
async def test_account_network_error_does_not_echo_url(operation, caplog):
    """Raw exception strings can contain authorization or household URLs."""
    session = SimpleNamespace(post=lambda *a, **kw: Response(error=aiohttp.ClientError(CANARY)))
    account = FlinxAccount(CANARY, CANARY)
    if operation == "get_token":
        assert await account.async_get_token(session) is None
    else:
        with pytest.raises(CannotConnect):
            if operation == "login":
                await account.async_login(session)
            else:
                await account.async_query_devices(session, CANARY)
    assert CANARY not in caplog.text


async def test_successful_login_retains_one_cached_session(caplog):
    account = FlinxAccount(CANARY, CANARY)
    requests = []

    def post(*args, **kwargs):
        requests.append(kwargs["json"])
        return Response({"code": 200, "data": {"token": CANARY}})

    session = SimpleNamespace(post=post)
    assert await account.async_login(session) == CANARY
    assert await account.async_get_token(session) == CANARY
    assert len(requests) == 1
    assert CANARY not in caplog.text


async def test_device_query_preserves_keys_and_identity_privately(caplog):
    device = {"deviceCode": CANARY, "devKey": FAKE_KEY, "bluetoothName": CANARY}
    session = SimpleNamespace(post=lambda *a, **kw: Response({"code": 200, "data": [device]}))
    account = FlinxAccount(CANARY, CANARY)
    assert await account.async_query_devices(session, CANARY) == [device]
    assert CANARY not in caplog.text
    assert FAKE_KEY not in caplog.text


def mqtt_client():
    return mqtt_module.FlinxMqttClient(
        asyncio.new_event_loop(), CANARY, FAKE_KEY, lambda attrs: None
    )


def test_mqtt_subscription_does_not_log_device_topic(caplog):
    """A topic embeds the private door identifier."""
    client = mqtt_client()
    try:
        client._on_connect(Mock(), None, None, 0)
        assert client.is_connected
        assert CANARY not in caplog.text
    finally:
        client._loop.close()


@pytest.mark.parametrize("plaintext", [None, CANARY.encode()])
def test_invalid_mqtt_message_does_not_log_payload_or_topic(plaintext, monkeypatch, caplog):
    """Undecodable frames must not be dumped to debug logs."""
    client = mqtt_client()
    monkeypatch.setattr(mqtt_module, "decrypt", lambda *a: plaintext)
    msg = SimpleNamespace(topic=f"/{CANARY}/attr/up", payload=b"fabricated")
    try:
        client._on_message(None, None, msg)
        assert CANARY not in caplog.text
        assert CANARY.encode().hex() not in caplog.text
    finally:
        client._loop.close()


def test_mqtt_metadata_is_delivered_without_logging_values(monkeypatch, caplog):
    """Redaction must preserve parsed state while concealing device metadata."""
    client = mqtt_client()
    received = []
    client._on_attrs = received.append
    attrs = {9984: CANARY, 10012: 42}
    monkeypatch.setattr(mqtt_module, "decrypt", lambda *a: b"fabricated")
    monkeypatch.setattr(mqtt_module, "parse_attr_report", lambda *a: attrs)
    try:
        client._on_message(None, None, SimpleNamespace(topic="/example/attr/up", payload=b""))
        assert received == [{9984: CANARY, 10012: 42}]
        assert client.last_message_ts > 0
        assert CANARY not in caplog.text
    finally:
        client._loop.close()


def cloud_coordinator(monkeypatch, response):
    coordinator = object.__new__(FlinxGarageCoordinator)
    coordinator.hass = None
    coordinator._cloud_enabled = True
    coordinator._device_code = CANARY
    coordinator._account = SimpleNamespace(
        async_get_token=AsyncMock(return_value="fabricated-session"),
        async_invalidate_token=lambda: None,
    )
    session = SimpleNamespace(get=lambda *a, **kw: response, post=lambda *a, **kw: response)
    monkeypatch.setattr(coordinator_module, "async_get_clientsession", lambda *a: session)
    return coordinator


async def test_cloud_rejection_does_not_echo_server_text(monkeypatch, caplog):
    """A gateway response can echo a private identifier into HA errors."""
    coordinator = cloud_coordinator(monkeypatch, Response({"code": 400, "msg": CANARY}))
    assert await coordinator._send_cloud_command(4097) is False
    assert CANARY not in caplog.text
    assert CANARY not in coordinator._last_command_error


async def test_cloud_network_error_does_not_echo_request_url(monkeypatch, caplog):
    coordinator = cloud_coordinator(monkeypatch, Response(error=aiohttp.ClientError(CANARY)))
    assert await coordinator._send_cloud_command(4097) is False
    assert CANARY not in caplog.text
    assert CANARY not in coordinator._last_command_error


@pytest.mark.parametrize("server_message", ["Device is offline", "Too frequent operation"])
async def test_known_cloud_rejections_remain_useful(server_message, monkeypatch):
    coordinator = cloud_coordinator(monkeypatch, Response({"code": 400, "msg": server_message}))
    assert await coordinator._send_cloud_command(4097) is False
    assert server_message.lower() in coordinator._last_command_error.lower()


async def test_successful_cloud_command_still_returns_success(monkeypatch):
    coordinator = cloud_coordinator(monkeypatch, Response({"code": 200, "data": {}}))
    assert await coordinator._send_cloud_command(4097) is True


def test_ble_metadata_is_applied_without_logging_values(monkeypatch, caplog):
    coordinator = object.__new__(FlinxGarageCoordinator)
    coordinator._dev_key = FAKE_KEY
    coordinator._ble_frame = bytearray()
    applied = []
    coordinator._apply_attrs = applied.append
    attrs = {9984: CANARY, 10012: 42}
    monkeypatch.setattr(coordinator_module, "unwrap_ble_frame", lambda *a: b"fabricated")
    monkeypatch.setattr(coordinator_module, "parse_attr_report", lambda *a: attrs)
    coordinator._ble_notification(0, b"\x55\x55fabricated")
    assert applied == [{9984: CANARY, 10012: 42}]
    assert CANARY not in caplog.text


@pytest.mark.parametrize("identified", [False, True])
def test_ble_discovery_keeps_matching_without_logging_identity(identified, caplog):
    coordinator = object.__new__(FlinxGarageCoordinator)
    name = f"Noru_{CANARY}"
    coordinator._ble_name = name if identified else None
    coordinator._ble_autodetect = True
    coordinator._door_alias = CANARY
    device = object()
    info = SimpleNamespace(name=name, address=CANARY, rssi=-60, source=CANARY, device=device)
    assert coordinator._match_ble_device([info]) is device
    assert CANARY not in caplog.text
