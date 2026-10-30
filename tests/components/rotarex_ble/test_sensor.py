"""Tests for the Rotarex DIMES SRG Bluetooth sensors."""

import pytest
from pytest_homeassistant.common import MockConfigEntry, snapshot_platform
from pytest_homeassistant.components.bluetooth import (
    inject_bluetooth_service_info_bleak,
)
from syrupy.assertion import SnapshotAssertion

from homeassistant.components.rotarex_ble.const import CONF_TANK_TYPE
from homeassistant.const import CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from . import DIMES_SERVICE_INFO

LEVEL_ENTITY_ID = "sensor.dimes_wave_eeff_level"


@pytest.mark.usefixtures("entity_registry_enabled_by_default")
async def test_sensors(
    hass: HomeAssistant,
    entity_registry: er.EntityRegistry,
    snapshot: SnapshotAssertion,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the sensors created from a captured advertisement."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()
    assert not hass.states.async_all("sensor")

    inject_bluetooth_service_info_bleak(hass, DIMES_SERVICE_INFO)
    await hass.async_block_till_done()

    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize(
    "tank_settings", [{CONF_REGION: "other", CONF_TANK_TYPE: "camping_tank"}]
)
async def test_level_follows_tank_settings(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test the level uses the tank settings of the config entry."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    inject_bluetooth_service_info_bleak(hass, DIMES_SERVICE_INFO)
    await hass.async_block_till_done()

    # A camping tank adds 1 to the raw level of 20, unlike the default settings
    assert (state := hass.states.get(LEVEL_ENTITY_ID))
    assert state.state == "21"
