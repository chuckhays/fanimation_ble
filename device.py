"""Fanimation BLE device communication."""
import asyncio
import logging

from bleak import BleakClient
from bleak.exc import BleakError

from .const import (
    FAN_CONTROL_CHARACTERISTIC_UUID,
    LIGHT_CONTROL_CHARACTERISTIC_UUID,
)

_LOGGER = logging.getLogger(__name__)


class FanimationBleDevice:
    """A wrapper for the Fanimation BLE device."""

    def __init__(self, address: str):
        """Initialize the device."""
        self.address = address
        self._client: BleakClient | None = None
        self.is_on = False
        self.light_is_on = False
        self.percentage = 0

    async def _write_gatt_char(self, uuid: str, data: bytearray):
        """Write a value to a BLE characteristic."""
        if not self._client or not self._client.is_connected:
            _LOGGER.warning("Attempted to write when not connected.")
            return
        try:
            await self._client.write_gatt_char(uuid, data, response=True)
        except BleakError as e:
            _LOGGER.error("Error writing to characteristic %s: %s", uuid, e)

    async def connect(self) -> bool:
        """Connect to the BLE device."""
        self._client = BleakClient(self.address)
        try:
            await self._client.connect()
            _LOGGER.info("Connected to %s", self.address)
            return True
        except (BleakError, asyncio.TimeoutError) as e:
            _LOGGER.error("Failed to connect to %s: %s", self.address, e)
            self._client = None
            return False

    async def disconnect(self):
        """Disconnect from the BLE device."""
        if self._client and self._client.is_connected:
            await self._client.disconnect()
        self._client = None

    async def set_fan_speed(self, percentage: int):
        """Set the fan speed."""
        # --- PLACEHOLDER ---
        # You must determine the correct byte command for your fan's speed.
        # This is just an example. It might be a single byte, or a command string.
        value_to_write = bytearray([percentage])
        await self._write_gatt_char(FAN_CONTROL_CHARACTERISTIC_UUID, value_to_write)

    async def set_light_power(self, is_on: bool):
        """Turn the light on or off."""
        # --- PLACEHOLDER ---
        # This is an example. It might be a command like `b'\x01'` for on and `b'\x00'` for off.
        value_to_write = bytearray([0x01 if is_on else 0x00])
        await self._write_gatt_char(LIGHT_CONTROL_CHARACTERISTIC_UUID, value_to_write)