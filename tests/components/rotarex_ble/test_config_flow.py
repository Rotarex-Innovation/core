"""Tests for the Rotarex DIMES Bluetooth config flow."""

from unittest.mock import AsyncMock, patch

from home_assistant_bluetooth import BluetoothServiceInfoBleak
import pytest
from pytest_homeassistant.common import MockConfigEntry

from homeassistant.components.rotarex_ble.const import CONF_TANK_TYPE, DOMAIN
from homeassistant.config_entries import SOURCE_BLUETOOTH, SOURCE_USER
from homeassistant.const import CONF_ADDRESS, CONF_REGION
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from . import (
    DIMES_ADDRESS,
    DIMES_PASSIVE_SERVICE_INFO,
    DIMES_SERVICE_INFO,
    DIMES_TITLE,
    NOT_DIMES_SERVICE_INFO,
)

DISCOVERY = (
    "homeassistant.components.rotarex_ble.config_flow.async_discovered_service_info"
)
SETTINGS = {CONF_REGION: "other", CONF_TANK_TYPE: "camping_tank"}


@pytest.mark.usefixtures("mock_setup_entry")
@pytest.mark.parametrize(
    "service_info",
    [
        pytest.param(DIMES_SERVICE_INFO, id="active_scan"),
        pytest.param(DIMES_PASSIVE_SERVICE_INFO, id="passive_scan"),
    ],
)
async def test_bluetooth_discovery(
    hass: HomeAssistant, service_info: BluetoothServiceInfoBleak
) -> None:
    """Test Bluetooth discovery asks for the tank settings."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=service_info
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "bluetooth_confirm"

    result = await hass.config_entries.flow.async_configure(result["flow_id"], SETTINGS)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == DIMES_TITLE
    assert result["data"] == {}
    assert result["options"] == SETTINGS
    assert result["result"].unique_id == DIMES_ADDRESS


async def test_bluetooth_discovery_not_supported(hass: HomeAssistant) -> None:
    """Test Bluetooth discovery rejects other devices."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=NOT_DIMES_SERVICE_INFO
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "not_supported"


async def test_bluetooth_discovery_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test Bluetooth discovery of a sensor that is already set up."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_BLUETOOTH}, data=DIMES_SERVICE_INFO
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.usefixtures("mock_setup_entry")
async def test_user_flow(hass: HomeAssistant) -> None:
    """Test picking a discovered sensor."""
    with patch(DISCOVERY, return_value=[NOT_DIMES_SERVICE_INFO, DIMES_SERVICE_INFO]):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_ADDRESS: DIMES_ADDRESS, **SETTINGS}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == DIMES_TITLE
    assert result["data"] == {}
    assert result["options"] == SETTINGS
    assert result["result"].unique_id == DIMES_ADDRESS


async def test_user_flow_no_devices(hass: HomeAssistant) -> None:
    """Test the user flow without any sensor in range."""
    with patch(DISCOVERY, return_value=[]):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_devices_found"


async def test_user_flow_skips_configured_sensor(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test sensors that are already set up are not offered again."""
    mock_config_entry.add_to_hass(hass)

    with patch(DISCOVERY, return_value=[DIMES_SERVICE_INFO]):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_devices_found"


async def test_user_flow_configured_while_open(hass: HomeAssistant) -> None:
    """Test the sensor gets set up elsewhere while the user flow is open."""
    with patch(DISCOVERY, return_value=[DIMES_SERVICE_INFO]):
        result = await hass.config_entries.flow.async_init(
            DOMAIN, context={"source": SOURCE_USER}
        )
    MockConfigEntry(domain=DOMAIN, unique_id=DIMES_ADDRESS).add_to_hass(hass)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_ADDRESS: DIMES_ADDRESS, **SETTINGS}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_options_flow(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_setup_entry: AsyncMock,
) -> None:
    """Test changing the tank settings."""
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], SETTINGS
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert mock_config_entry.options == SETTINGS
    assert len(mock_setup_entry.mock_calls) == 2
