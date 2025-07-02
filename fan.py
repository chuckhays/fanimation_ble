"""Fan platform for Fanimation BLE."""
from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
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
    """Set up the fan entity."""
    device: FanimationBleDevice = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FanimationBleFanEntity(device)])


class FanimationBleFanEntity(FanimationBleEntity, FanEntity):
    """Representation of a Fanimation BLE fan."""

    _attr_supported_features = FanEntityFeature.SET_SPEED
    _attr_speed_count = 3  # Example: 3 speeds (low, medium, high)

    def __init__(self, device: FanimationBleDevice) -> None:
        """Initialize the fan entity."""
        super().__init__(device, "Fanimation Fan", "fan")

    @property
    def is_on(self) -> bool | None:
        """Return true if the fan is on."""
        return self._device.is_on

    @property
    def percentage(self) -> int | None:
        """Return the current speed percentage."""
        return self._device.percentage

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan."""
        await self._device.set_fan_speed(percentage)
        self._device.percentage = percentage
        self._device.is_on = percentage > 0
        self.async_write_ha_state()

    async def async_turn_on(self, percentage: int | None = None, **kwargs: Any) -> None:
        """Turn the fan on."""
        await self.async_set_percentage(percentage or 50)  # Default to 50% speed

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self.async_set_percentage(0)