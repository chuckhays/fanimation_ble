"""Light platform for Fanimation BLE."""
from __future__ import annotations

from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS, ColorMode, LightEntity
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

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(self, device: FanimationBleDevice) -> None:
        """Initialize the light entity."""
        super().__init__(device, "Fanimation Light", "light")

    @property
    def is_on(self) -> bool | None:
        """Return true if the light is on."""
        return self._device.light_is_on

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        return self._device.brightness

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the light on."""
        brightness = kwargs.get(ATTR_BRIGHTNESS, 255)
        await self._device.set_light_brightness(brightness)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the light off."""
        await self._device.set_light_brightness(0)