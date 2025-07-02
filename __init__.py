"""The Fanimation BLE integration."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN
from .device import FanimationBleDevice

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.FAN, Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Fanimation BLE from a config entry."""
    address = entry.data[CONF_ADDRESS]
    _LOGGER.debug("Setting up Fanimation BLE device at address %s", address)

    # Create a single device object to be shared by all entities
    device = FanimationBleDevice(address)
    if not await device.connect():
        raise ConfigEntryNotReady(f"Could not connect to BLE device at {address}")

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = device

    # Forward the setup to the fan and light platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        device: FanimationBleDevice = hass.data[DOMAIN].pop(entry.entry_id)
        await device.disconnect()

    return unload_ok