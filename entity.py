"""Base entity for Fanimation BLE."""
from homeassistant.helpers.entity import DeviceInfo, Entity

from .const import DOMAIN
from .device import FanimationBleDevice


class FanimationBleEntity(Entity):
    """Representation of a Fanimation BLE entity."""

    def __init__(self, device: FanimationBleDevice, name: str, unique_id_suffix: str):
        """Initialize the entity."""
        self._device = device
        self._attr_name = name
        self._attr_unique_id = f"{device.address}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device.address)},
            name=name,
            manufacturer="Fanimation",
            model="Smart Fan",
        )