"""Constants for the Fanimation BLE integration."""

DOMAIN = "fanimation_ble"

# --- PLACEHOLDERS ---
# Replace these with the actual UUIDs from your device.
# You can find these using a BLE scanner app like nRF Connect.

FANIMATION_SERVICE_UUID = "0000fee7-0000-1000-8000-00805f9b34fb"  # Example Service UUID
FAN_CONTROL_CHARACTERISTIC_UUID = "0000fec8-0000-1000-8000-00805f9b34fb"  # Example Characteristic for Fan
LIGHT_CONTROL_CHARACTERISTIC_UUID = "0000fec9-0000-1000-8000-00805f9b34fb" # Example Characteristic for Light