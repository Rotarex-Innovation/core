"""Config flow for the Rotarex DIMES SRG Bluetooth integration."""

from typing import TYPE_CHECKING, Any, override

import probatio
from rotarex_dimes_ble import Region, RotarexDimesBluetoothDeviceData as DeviceData

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.const import CONF_ADDRESS, CONF_REGION
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from . import RotarexBleConfigEntry
from .const import CONF_TANK_TYPE, DEFAULT_REGION, DEFAULT_TANK_TYPE, DOMAIN, TANK_TYPES

SETTINGS_SCHEMA = probatio.Schema(
    {
        probatio.Required(CONF_REGION, default=DEFAULT_REGION): SelectSelector(
            SelectSelectorConfig(
                options=list(Region),
                mode=SelectSelectorMode.DROPDOWN,
                translation_key=CONF_REGION,
            )
        ),
        probatio.Required(CONF_TANK_TYPE, default=DEFAULT_TANK_TYPE): SelectSelector(
            SelectSelectorConfig(
                options=TANK_TYPES,
                mode=SelectSelectorMode.DROPDOWN,
                translation_key=CONF_TANK_TYPE,
            )
        ),
    }
)


class RotarexBleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Rotarex Dimes Wave sensors."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovered_title: str | None = None
        self._discovered_devices: dict[str, str] = {}

    @staticmethod
    @callback
    @override
    def async_get_options_flow(
        config_entry: RotarexBleConfigEntry,
    ) -> RotarexBleOptionsFlow:
        """Return the options flow."""
        return RotarexBleOptionsFlow()

    @override
    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> ConfigFlowResult:
        """Handle the Bluetooth discovery step."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()
        device = DeviceData()
        if not device.supported(discovery_info):
            return self.async_abort(reason="not_supported")
        self._discovered_title = device.title
        return await self.async_step_bluetooth_confirm()

    async def async_step_bluetooth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm discovery and select the tank settings."""
        title = self._discovered_title
        if TYPE_CHECKING:
            assert title is not None
        if user_input is not None:
            return self.async_create_entry(title=title, data={}, options=user_input)

        placeholders = {"name": title}
        self.context["title_placeholders"] = placeholders
        return self.async_show_form(
            step_id="bluetooth_confirm",
            data_schema=SETTINGS_SCHEMA,
            description_placeholders=placeholders,
        )

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the user step to pick a discovered sensor."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            settings = {
                key: value for key, value in user_input.items() if key != CONF_ADDRESS
            }
            return self.async_create_entry(
                title=self._discovered_devices[address], data={}, options=settings
            )

        current_addresses = self._async_current_ids(include_ignore=False)
        for discovery_info in async_discovered_service_info(self.hass, False):
            address = discovery_info.address
            if address in current_addresses or address in self._discovered_devices:
                continue
            device = DeviceData()
            if device.supported(discovery_info) and device.title:
                self._discovered_devices[address] = device.title

        if not self._discovered_devices:
            return self.async_abort(reason="no_devices_found")

        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema(
                {
                    probatio.Required(CONF_ADDRESS): probatio.In(
                        self._discovered_devices
                    ),
                    **SETTINGS_SCHEMA.schema,
                }
            ),
        )


class RotarexBleOptionsFlow(OptionsFlowWithReload):
    """Handle the tank settings of a Rotarex Dimes Wave sensor."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Manage the tank settings."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                SETTINGS_SCHEMA, self.config_entry.options
            ),
        )
