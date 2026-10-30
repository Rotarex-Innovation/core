"""Tests for the Rotarex DIMES SRG Bluetooth integration."""

from pytest_homeassistant.components.bluetooth import (
    generate_advertisement_data,
    generate_ble_device,
)

from homeassistant.components.bluetooth import BluetoothServiceInfoBleak

SERVICE_UUID = "2b67836a-183d-45da-a1bf-381b05e1bde8"

DIMES_ADDRESS = "AA:BB:CC:DD:EE:FF"
DIMES_TITLE = "Dimes Wave EEFF"
# Captured from a real sensor: battery 89 %, raw level 20 %
DIMES_PAYLOAD = bytes.fromhex("00591414")


def make_service_info(
    payload: bytes = DIMES_PAYLOAD,
    local_name: str | None = "SRG-1-WAVE",
    address: str = DIMES_ADDRESS,
    service_uuids: list[str] | None = None,
) -> BluetoothServiceInfoBleak:
    """Return the service info of a Dimes Wave advertisement."""
    manufacturer_data = {0xFFFF: payload}
    service_uuids = [SERVICE_UUID] if service_uuids is None else service_uuids
    return BluetoothServiceInfoBleak(
        # Home Assistant uses the address as name without a local name
        name=local_name or address,
        address=address,
        device=generate_ble_device(address, local_name),
        rssi=-69,
        manufacturer_data=manufacturer_data,
        service_data={},
        service_uuids=service_uuids,
        source="local",
        advertisement=generate_advertisement_data(
            local_name=local_name,
            manufacturer_data=manufacturer_data,
            service_uuids=service_uuids,
        ),
        time=0,
        connectable=False,
        tx_power=-127,
    )


DIMES_SERVICE_INFO = make_service_info()
# Passive scans don't get the scan response with the local name
DIMES_PASSIVE_SERVICE_INFO = make_service_info(local_name=None)
# Sent right after a battery change, before the first measurement
DIMES_RESET_SERVICE_INFO = make_service_info(payload=bytes(4))
NOT_DIMES_SERVICE_INFO = make_service_info(
    local_name="Not it", address="00:00:00:00:00:01", service_uuids=[]
)
