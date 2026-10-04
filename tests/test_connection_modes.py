"""Preserve transport selection and fallbacks without actuating anything."""

import pytest

from custom_components.flinx_garage.coordinator import FlinxGarageCoordinator


@pytest.mark.parametrize(
    "mode,ble_ok,cloud_ok,wait_ok,want_ok,want_events",
    [
        ("ble_only", True, True, False, True, ["ble", "refresh"]),
        ("ble_only", False, True, False, False, ["ble", "wait"]),
        ("cloud_only", True, True, False, True, ["cloud", "refresh"]),
        ("cloud_only", True, False, False, False, ["cloud"]),
        ("ble_preferred", True, True, False, True, ["ble", "refresh"]),
        ("ble_preferred", False, True, False, True, ["ble", "cloud", "refresh"]),
        ("ble_preferred", False, False, False, False, ["ble", "cloud", "wait"]),
        ("cloud_preferred", True, True, False, True, ["cloud", "refresh"]),
        ("cloud_preferred", True, False, True, True, ["cloud", "wait", "ble", "refresh"]),
        ("cloud_preferred", False, False, True, False, ["cloud", "wait", "ble"]),
    ],
)
async def test_transport_selection(mode, ble_ok, cloud_ok, wait_ok, want_ok, want_events):
    coordinator = object.__new__(FlinxGarageCoordinator)
    coordinator._connection_mode = mode
    events = []

    async def ble(command):
        assert command == 1
        events.append("ble")
        return ble_ok

    async def cloud(command):
        assert command == 4097
        events.append("cloud")
        return cloud_ok

    async def wait(timeout):
        events.append("wait")
        return wait_ok

    coordinator._send_ble_command = ble
    coordinator._send_cloud_command = cloud
    coordinator._async_wait_for_ble = wait
    coordinator._schedule_post_command_refresh = lambda target: events.append("refresh")

    assert await coordinator._send_command(1, 4097, target_position=100) is want_ok
    assert events == want_events
