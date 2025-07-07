"""Config flow for Fanimation BLE."""
import voluptuous as vol
import logging

from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak,
    async_discovered_service_info,
)
from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_ADDRESS

from .const import DOMAIN, FANIMATION_SERVICE_UUID

_LOGGER = logging.getLogger(__name__)


class FanimationBleConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fanimation BLE."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._discovery_info: BluetoothServiceInfoBleak | None = None
        _LOGGER.debug("FanimationBleConfigFlow initialized")

    async def async_step_user(self, user_input=None):
        """Handle the user step to select a device."""
        _LOGGER.debug("async_step_user called with user_input: %s", user_input)
        if user_input is not None:
            address = user_input[CONF_ADDRESS]
            _LOGGER.debug("User selected address: %s", address)
            await self.async_set_unique_id(address, raise_on_progress=False)
            self._abort_if_unique_id_configured()
            _LOGGER.debug("Creating entry for address: %s", address)
            return self.async_create_entry(
                title=user_input["name"], data={CONF_ADDRESS: address}
            )

        current_addresses = self._async_current_entries()
        _LOGGER.debug("Current addresses: %s", current_addresses)
        for discovery_info in async_discovered_service_info(self.hass):
            _LOGGER.debug("Discovered device: %s", discovery_info)
            if discovery_info.address in current_addresses:
                _LOGGER.debug(
                    "Device %s already configured, skipping", discovery_info.address
                )
                continue

            if FANIMATION_SERVICE_UUID in discovery_info.service_uuids:
                _LOGGER.debug(
                    "Device %s matches service UUID, proceeding to bluetooth step",
                    discovery_info.address,
                )
                return await self.async_step_bluetooth(discovery_info)

        _LOGGER.debug("No devices found, aborting flow")
        return self.async_abort(reason="no_devices_found")

    async def async_step_bluetooth(
        self, discovery_info: BluetoothServiceInfoBleak
    ) -> dict:
        """Handle discovery via Bluetooth."""
        _LOGGER.debug(
            "async_step_bluetooth called with discovery_info: %s", discovery_info
        )
        await self.async_set_unique_id(discovery_info.address)
        self._abort_if_unique_id_configured()

        if FANIMATION_SERVICE_UUID not in discovery_info.service_uuids:
            _LOGGER.debug(
                "Device %s does not support required service UUID, aborting",
                discovery_info.address,
            )
            return self.async_abort(reason="not_supported")

        self.context["title_placeholders"] = {"name": discovery_info.name}
        _LOGGER.debug(
            "Creating entry for discovered device: %s", discovery_info.name
        )
        return self.async_create_entry(
            title=discovery_info.name,
            data={CONF_ADDRESS: discovery_info.address},
        )