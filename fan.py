"""Fan platform for Fanimation BLE."""
from __future__ import annotations

from typing import Any, Optional

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.percentage import (
    int_states_in_range,
    percentage_to_ranged_value,
    ranged_value_to_percentage,
)

from .const import DOMAIN
from .device import FanimationBleDevice
from .entity import FanimationBleEntity

SPEED_RANGE = (1, 31)  # The fan uses a 1-31 speed range


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

    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.DIRECTION
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )

    def __init__(self, device: FanimationBleDevice) -> None:
        """Initialize the fan entity."""
        super().__init__(device, "Fanimation Fan", "fan")

    @property
    def is_on(self) -> bool | None:
        """Return true if the fan is on."""
        return self._device.is_on

    @property
    def percentage(self) -> Optional[int]:
        """Return the current speed percentage."""
        if self._device.percentage is None or self._device.percentage == 0:
            return 0
        return ranged_value_to_percentage(SPEED_RANGE, self._device.percentage)

    @property
    def speed_count(self) -> int:
        """Return the number of speeds the fan supports."""
        return int_states_in_range(SPEED_RANGE)

    @property
    def current_direction(self) -> str | None:
        """Return the current direction of the fan."""
        return "reverse" if self._device.direction == 1 else "forward"

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan."""
        if percentage == 0:
            speed = 0
        else:
            speed = round(percentage_to_ranged_value(SPEED_RANGE, percentage))
        await self._device.set_fan_speed(int(speed))

    async def async_set_direction(self, direction: str) -> None:
        """Set the direction of the fan."""
        direction_val = 1 if direction == "reverse" else 0
        await self._device.set_direction(direction_val)

    async def async_turn_on(self, percentage: int | None = None, **kwargs: Any) -> None:
        """Turn the fan on."""
        await self.async_set_percentage(percentage or 50)  # Default to 50% speed

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the fan off."""
        await self.async_set_percentage(0)