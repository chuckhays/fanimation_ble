"""Fanimation BLE device communication."""
import asyncio
import logging

from bleak import BleakClient
from bleak.exc import BleakError

from .const import COMMAND_WRITE_UUID, STATUS_NOTIFY_UUID

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
        self._update_callback = None

    def register_callback(self, callback) -> None:
        """Register a callback to be called when the state changes."""
        self._update_callback = callback

    def _notification_handler(self, sender: int, data: bytearray):
        """Handle notification responses."""
        _LOGGER.debug("Received notification: %s", data.hex())
        # --- PLACEHOLDER ---
        # You must parse the `data` bytearray to update the device state.
        # This is a placeholder implementation.
        # For example, if byte 0 is the command type and byte 1 is the value:
        if data[0] == 0x01:  # Fan status update
            self.percentage = data[1]
            self.is_on = self.percentage > 0
        elif data[0] == 0x02:  # Light status update
            self.light_is_on = data[1] == 0x01

        if self._update_callback:
            self._update_callback()

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
            await self._client.start_notify(
                STATUS_NOTIFY_UUID, self._notification_handler
            )
            _LOGGER.info("Connected to %s", self.address)
            return True
        except (BleakError, asyncio.TimeoutError) as e:
            _LOGGER.error("Failed to connect to %s: %s", self.address, e)
            self._client = None
            return False

    async def disconnect(self):
        """Disconnect from the BLE device."""
        if self._client and self._client.is_connected:
            try:
                await self._client.stop_notify(STATUS_NOTIFY_UUID)
            except BleakError as e:
                _LOGGER.warning("Failed to stop notifications: %s", e)
            await self._client.disconnect()
        self._client = None

    async def set_fan_speed(self, percentage: int):
        """Set the fan speed."""
        # --- PLACEHOLDER ---
        # Example: Command byte 0x01 for fan, followed by speed
        value_to_write = bytearray([0x01, percentage])
        await self._write_gatt_char(COMMAND_WRITE_UUID, value_to_write)

    async def set_light_power(self, is_on: bool):
        """Turn the light on or off."""
        # --- PLACEHOLDER ---
        # Example: Command byte 0x02 for light, followed by state
        value_to_write = bytearray([0x02, 0x01 if is_on else 0x00])
        await self._write_gatt_char(COMMAND_WRITE_UUID, value_to_write)