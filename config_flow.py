"""Config flow for Fanimation BLE."""
import voluptuous as vol

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, FANIMATION_SERVICE_UUID


class FanimationBleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fanimation BLE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None

    async def async_step_user(self, user_input=None):
        """Handle the user step to select a device."""
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input["name"], data={CONF_ADDRESS: address}
            )

        current_addresses = self._async_current_entries()
        for discovery_info in async_discovered_service_info(self.hass):
            if discovery_info.address in current_addresses:
                continue

            if FANIMATION_SERVICE_UUID in discovery_info.service_uuids:
                return await self.async_step_bluetooth(discovery_info)

        return self.async_abort(reason="no_devices_found")

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> dict:
        """Handle discovery via Bluetooth."""
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        if FANIMATION_SERVICE_UUID not in discovery_info.service_uuids:
            return self.async_abort(reason="not_supported")

        self.context["title_placeholders"] = {"name": discovery_info.name}
        return self.async_create_entry(
            title=discovery_info.name,
            data={CONF_ADDRESS: discovery_info.address},
        )