"""Light platform for Fanimation BLE."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ColorMode, LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .device import FanimationBleDevice
from .entity import FanimationBleEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light entity."""
    device: FanimationBleDevice = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FanimationBleLightEntity(device)])


class FanimationBleLightEntity(FanimationBleEntity, LightEntity):
    """Representation of a Fanimation BLE light."""

    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}

    def __init__(self, device: FanimationBleDevice) -> None:
        """Initialize the light entity."""
        super().__init__(device, "Fanimation Light", "light")

    @property
    def is_on(self) -> bool | None:
        """Return true if the light is on."""
        return self._device.light_is_on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        await self._device.set_light_power(True)
        self._device.light_is_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self._device.set_light_power(False)
        self._device.light_is_on = False
        self.async_write_ha_state()