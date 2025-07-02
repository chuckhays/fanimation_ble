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
        self.brightness = 0
        self.direction = 0  # 0 for forward, 1 for reverse
        self.timer_minutes = 0
        self._update_callback = None

    def register_callback(self, callback) -> None:
        """Register a callback to be called when the state changes."""
        self._update_callback = callback

    def _notification_handler(self, sender: int, data: bytearray):
        """Handle notification responses."""
        _LOGGER.debug("Received notification: %s", data.hex())

        # Verify checksum of received data
        if len(data) != 9 or (sum(data[:-1]) & 0xFF) != data[8]:
            _LOGGER.warning(
                "Received notification with invalid checksum or length: %s", data.hex()
            )
            return
        
        # --- PLACEHOLDER ---
        # Assuming the notification format matches the command structure
        # Byte 0 should be 0x53, Byte 1 should be command type
        self.percentage = data[2]
        self.is_on = self.percentage > 0
        self.direction = data[3]
        # Byte 4 is constant 0
        self.brightness = data[5]
        self.light_is_on = self.brightness > 0
        self.timer_minutes = data[6]
        # Byte 7 is constant 0

        if self._update_callback:
            self._update_callback()

    def _compute_checksum(self, payload: bytearray) -> int:
        """Compute the checksum for a command payload."""
        return sum(payload) & 0xFF

    def _create_command_packet(self, command_type: int) -> bytearray:
        """Creates a 9-byte command packet."""
        payload = bytearray(8)  # Create an 8-byte array, checksum will be 9th
        payload[0] = 0x53
        payload[1] = command_type

        if command_type == 0x31:  # Write command
            payload[2] = self.percentage
            payload[3] = self.direction
            payload[4] = 0
            payload[5] = self.brightness
            payload[6] = self.timer_minutes
            payload[7] = 0
        # For a read command (0x30), bytes 2-7 are already initialized to 0

        checksum = sum(payload) & 0xFF
        return payload + bytearray([checksum])

    async def _send_command(self, command: bytearray):
        """Writes a command to the BLE characteristic."""
        if not self._client or not self._client.is_connected:
            _LOGGER.warning("Attempted to write when not connected.")
            return
        try:
            _LOGGER.debug("Sending command: %s", command.hex())
            await self._client.write_gatt_char(
                COMMAND_WRITE_UUID, command, response=False
            )
        except BleakError as e:
            _LOGGER.error(
                "Error writing to characteristic %s: %s", COMMAND_WRITE_UUID, e
            )


    async def connect(self) -> bool:
        """Connect to the BLE device."""
        self._client = BleakClient(self.address)
        try:
            await self._client.connect()
            await self._client.start_notify(
                STATUS_NOTIFY_UUID, self._notification_handler
            )
            await self.async_request_status()
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
        self.percentage = percentage
        command = self._create_command_packet(0x31)
        await self._send_command(command)

    async def set_light_brightness(self, brightness: int):
        """Set the light brightness."""
        self.brightness = brightness
        command = self._create_command_packet(0x31)
        await self._send_command(command)

    async def set_direction(self, direction: int):
        """Set the fan direction."""
        self.direction = direction
        command = self._create_command_packet(0x31)
        await self._send_command(command)

    async def async_request_status(self):
        """Request a status update from the device."""
        command = self._create_command_packet(0x30)
        await self._send_command(command)