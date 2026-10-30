"""The Rotarex DIMES SRG Bluetooth integration."""

import logging

from rotarex_dimes_ble import Region, RotarexDimesBluetoothDeviceData, TankType

from homeassistant.components.bluetooth import BluetoothScanningMode
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothProcessorCoordinator,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_REGION, Platform
from homeassistant.core import HomeAssistant

from .const import CONF_TANK_TYPE

PLATFORMS: list[Platform] = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

type RotarexBleConfigEntry = ConfigEntry[PassiveBluetoothProcessorCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: RotarexBleConfigEntry) -> None:
    """Set up a Rotarex Dimes Wave sensor from a config entry."""
    address = entry.unique_id
    assert address is not None

    data = RotarexDimesBluetoothDeviceData(
        Region(entry.options[CONF_REGION]), TankType(entry.options[CONF_TANK_TYPE])
    )
    coordinator = entry.runtime_data = PassiveBluetoothProcessorCoordinator(
        hass,
        _LOGGER,
        address=address,
        mode=BluetoothScanningMode.PASSIVE,
        update_method=data.update,
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    # Only start after all platforms have had a chance to subscribe
    entry.async_on_unload(coordinator.async_start())


async def async_unload_entry(hass: HomeAssistant, entry: RotarexBleConfigEntry) -> None:
    """Unload a config entry."""
    await hass.config_entries.async_unload_platforms_or_raise(entry, PLATFORMS)
