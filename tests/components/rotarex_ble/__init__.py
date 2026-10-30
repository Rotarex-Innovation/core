"""Tests for the Rotarex DIMES SRG Bluetooth integration."""

from home_assistant_bluetooth import BluetoothServiceInfoBleak
from pytest_homeassistant.components.bluetooth import (
    generate_advertisement_data,
    generate_ble_device,
)

from homeassistant.helpers.service_info.bluetooth import BluetoothServiceInfo

SERVICE_UUID = "2b67836a-183d-45da-a1bf-381b05e1bde8"

DIMES_ADDRESS = "AA:BB:CC:DD:EE:FF"
DIMES_TITLE = "Dimes Wave EEFF"
# Captured from a real sensor: battery 89 %, raw level 20 %
DIMES_MANUFACTURER_DATA = {0xFFFF: bytes.fromhex("00591414")}

DIMES_SERVICE_INFO = BluetoothServiceInfoBleak(
    name="SRG-1-WAVE",
    address=DIMES_ADDRESS,
    device=generate_ble_device(DIMES_ADDRESS, "SRG-1-WAVE"),
    rssi=-69,
    manufacturer_data=DIMES_MANUFACTURER_DATA,
    service_data={},
    service_uuids=[SERVICE_UUID],
    source="local",
    advertisement=generate_advertisement_data(
        local_name="SRG-1-WAVE",
        manufacturer_data=DIMES_MANUFACTURER_DATA,
        service_uuids=[SERVICE_UUID],
    ),
    time=0,
    connectable=False,
    tx_power=-127,
)

# Passive scans don't get the scan response with the local name
DIMES_PASSIVE_SERVICE_INFO = BluetoothServiceInfoBleak(
    name=DIMES_ADDRESS,
    address=DIMES_ADDRESS,
    device=generate_ble_device(DIMES_ADDRESS, None),
    rssi=-69,
    manufacturer_data=DIMES_MANUFACTURER_DATA,
    service_data={},
    service_uuids=[SERVICE_UUID],
    source="local",
    advertisement=generate_advertisement_data(
        manufacturer_data=DIMES_MANUFACTURER_DATA,
        service_uuids=[SERVICE_UUID],
    ),
    time=0,
    connectable=False,
    tx_power=-127,
)

NOT_DIMES_SERVICE_INFO = BluetoothServiceInfo(
    name="Not it",
    address="00:00:00:00:00:01",
    rssi=-63,
    manufacturer_data={0xFFFF: bytes.fromhex("00591414")},
    service_data={},
    service_uuids=[],
    source="local",
)
