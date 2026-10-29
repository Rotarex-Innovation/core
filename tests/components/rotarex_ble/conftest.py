"""Common fixtures for the Rotarex DIMES Bluetooth tests."""

from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from pytest_homeassistant.common import MockConfigEntry

from homeassistant.components.rotarex_ble.const import CONF_TANK_TYPE, DOMAIN
from homeassistant.const import CONF_REGION

from . import DIMES_ADDRESS, DIMES_TITLE


@pytest.fixture(autouse=True)
def mock_bluetooth(enable_bluetooth: None) -> None:
    """Auto mock bluetooth."""


@pytest.fixture
def mock_setup_entry() -> Generator[AsyncMock]:
    """Override async_setup_entry."""
    with patch(
        "homeassistant.components.rotarex_ble.async_setup_entry", return_value=None
    ) as mock_setup_entry:
        yield mock_setup_entry


@pytest.fixture
def mock_config_entry() -> MockConfigEntry:
    """Return a config entry for a camping cylinder in Europe."""
    return MockConfigEntry(
        domain=DOMAIN,
        title=DIMES_TITLE,
        unique_id=DIMES_ADDRESS,
        data={},
        options={CONF_REGION: "europe", CONF_TANK_TYPE: "camping_cylinder"},
    )
