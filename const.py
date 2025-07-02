"""Constants for the Fanimation BLE integration."""

DOMAIN = "fanimation_ble"

# --- PLACEHOLDERS ---
# Replace these with the actual UUIDs from your device.
# You can find these using a BLE scanner app like nRF Connect.

FANIMATION_SERVICE_UUID = "0000fee7-0000-1000-8000-00805f9b34fb" # Example Service UUID
COMMAND_WRITE_UUID = "0000e001-0000-1000-8000-00805f9b34fb"  # The characteristic for writing all commands
STATUS_NOTIFY_UUID = "0000e002-0000-1000-8000-00805f9b34fb"  # The characteristic for receiving status updates