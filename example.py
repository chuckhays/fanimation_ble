import asyncio
from bleak import BleakScanner, BleakClient

# --- Configuration ---
# Replace these with the actual name and characteristic UUID of your device
TARGET_DEVICE_NAME = "CeilingFan"
TARGET_CHARACTERISTIC_UUID_WRITE = "0000e001-0000-1000-8000-00805f9b34fb"
TARGET_CHARACTERISTIC_UUID_READ = "0000e002-0000-1000-8000-00805f9b34fb"

def compute_checksum(command):
    total = sum(command[:-1])
    return total & 0xFF

def create_command(command_type, fan_speed=0, fan_direction=0):
    command = bytearray(10)

    command[0] = 0x53
    command[1] = command_type
    command[2] = fan_speed
    command[3] = fan_direction
    command[4] = 0
    command[5] = 0
    command[6] = 0
    command[7] = 0
    command[8] = 0
    command[9] = compute_checksum(command)

    return command

def interpret_status(response):
    """
    Interprets the response bytes to determine fan status.

    Args:
        response: A bytes object or bytearray containing the response from the fan.
                  Assumes speed is at index 2 and direction is at index 3.

    Returns:
        A string describing the fan's status (power, speed, and direction).
    """
    # Interpret the response bytes
    speed = response[2]  # Assuming speed is at index 2
    direction = response[3]  # Assuming direction is at index 3
    is_on = speed > 0

    direction_str = "Forward" if direction == 0 else "Reverse"
    return f"Fan Status - Power: {'On' if is_on else 'Off'}, Speed: {speed}, Direction: {direction_str}"

async def main():
    """
    Scans for, connects to, and finds a specific characteristic on a BLE device.
    """
    print("Scanning for BLE devices... 🕵️")
    devices = await BleakScanner.discover()

    if not devices:
        print("No BLE devices found.")
        return

    # Find the target device by name
    target_device = None
    for device in devices:
        if device.name == TARGET_DEVICE_NAME:
            target_device = device
            break

    if not target_device:
        print(f"\n❌ Device with name '{TARGET_DEVICE_NAME}' not found.")
        return

    print(f"\nFound target device: {target_device.name} ({target_device.address})")
    print(f"Attempting to connect...")

    async with BleakClient(target_device.address) as client:
        if not client.is_connected:
            print(f"❌ Failed to connect to {target_device.name}.")
            return

        print(f"✅ Successfully connected to {target_device.name}!")

        # --- Find and save the target characteristic ---
        target_characteristic_write = None
        target_characteristic_read = None
        for service in client.services:
            for char in service.characteristics:
                if char.uuid == TARGET_CHARACTERISTIC_UUID_WRITE:
                    target_characteristic_write = char
                elif char.uuid == TARGET_CHARACTERISTIC_UUID_READ:
                    target_characteristic_read = char
            if target_characteristic_write and target_characteristic_read:
                break # Exit the outer loop once found

        if target_characteristic_write:
            print(f"\n🎯 Found Characteristic: {target_characteristic_write.uuid}")
            print(f"   Properties: {', '.join(target_characteristic_write.properties)}")

            # Now you can use the saved 'target_characteristic' object
            # For example, to read its value (if readable):
            if "read" in target_characteristic_write.properties:
                try:
                    value = await client.read_gatt_char(target_characteristic_write)
                    print(f"   Value (raw): {value.hex()}")
                except Exception as e:
                    print(f"   Error reading characteristic: {e}")
            else:
                print("   Characteristic is not readable.")

        else:
            print(f"\n❌ Characteristic with UUID {TARGET_CHARACTERISTIC_UUID_WRITE} not found.")

        if target_characteristic_read:
            print(f"\n🎯 Found Characteristic: {target_characteristic_read.uuid}")
            print(f"   Properties: {', '.join(target_characteristic_read.properties)}")

            # Now you can use the saved 'target_characteristic' object
            # For example, to read its value (if readable):
            # Subscribe to notifications for this characteristic
            def notification_handler(sender, data):
                print(f"🔔 Notification from {sender}: {data.hex()}")
                result = interpret_status(data)
                print(f"   Interpreted Status: {result}")

            if "notify" in target_characteristic_read.properties:
                print("   Subscribing to notifications...")
                await client.start_notify(target_characteristic_read, notification_handler)
                print("   Listening for notifications. Press Ctrl+C to exit.")
            elif "read" in target_characteristic_read.properties:
                try:
                    value = await client.read_gatt_char(target_characteristic_read)
                    print(f"   Value (raw): {value.hex()}")
                except Exception as e:
                    print(f"   Error reading characteristic: {e}")
            else:
                print("   Characteristic is not readable or notifiable.")

        else:
            print(f"\n❌ Characteristic with UUID {TARGET_CHARACTERISTIC_UUID_READ} not found.")

        if target_characteristic_write:
            # command = create_command(0x30)
            command = create_command(0x31, fan_speed=0x05, fan_direction=0x00)
            print(f"\nSending command to {target_characteristic_write.uuid}...")
            print(f"   Command (raw): {command.hex()}")
            await client.write_gatt_char(target_characteristic_write, command, response=True)
            print(f"\Sent command to {target_characteristic_write.uuid}...")
            #53300000000000000083
            #53300000000000000083

            await asyncio.sleep(15)
            print("Stopping notifications...")
            await client.stop_notify(target_characteristic_read)
            # try:
            #     while True:
            #         await asyncio.sleep(15)
            # except KeyboardInterrupt:
            #     print("\n   Stopping notifications.")
            #     await client.stop_notify(target_characteristic_read)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
