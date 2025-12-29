import asyncio
import struct
import time

from bleak import BleakClient
import RPi.GPIO as GPIO

from config_loader import CONFIG

# ========= CONFIG =========

DWM_MAC = CONFIG["ble"]["dwm_mac"]
LOCATION_MODE = CONFIG["ble"]["location_mode"]

LOCATION_MODE_CHAR_UUID = "a02b947e-df97-4516-996a-1882521e0ead"
LOCATION_DATA_CHAR_UUID = "003bbdf2-c634-4b3d-ab56-7ec889b89a37"

BUTTON_PIN = CONFIG["gpio"]["button_pin"]
GPIO_PULL = CONFIG["gpio"]["pull"]

PRINT_ON_BUTTON = CONFIG.get("logging", {}).get(
    "print_position_on_button", True
)

# ========= GLOBAL STATE =========
# (x_m, y_m, z_m, q, timestamp)
last_position = None

# ========= BLE HANDLERS =========

def handle_disconnect(client):
    print("[-] Disconnected from DWM1001")


def parse_location_data(data: bytes):
    global last_position

    if not data:
        return

    msg_type = data[0]
    offset = 1

    # Position present for type 0 or 2
    if msg_type in (0, 2):
        if len(data) < offset + 13:
            return

        x_mm, y_mm, z_mm = struct.unpack_from("<iii", data, offset)
        q = data[offset + 12]

        last_position = (
            x_mm / 1000.0,
            y_mm / 1000.0,
            z_mm / 1000.0,
            q,
            time.time()
        )


def notification_handler(sender, data: bytearray):
    parse_location_data(bytes(data))


# ========= BLE LOOP =========

async def ble_location_loop():
    while True:
        try:
            print("[BLE] Connecting to", DWM_MAC)
            async with BleakClient(
                DWM_MAC,
                disconnected_callback=handle_disconnect
            ) as client:

                print("[BLE] Connected")

                await client.write_gatt_char(
                    LOCATION_MODE_CHAR_UUID,
                    bytes([LOCATION_MODE]),
                    response=True
                )

                await client.start_notify(
                    LOCATION_DATA_CHAR_UUID,
                    notification_handler
                )

                while client.is_connected:
                    await asyncio.sleep(0.2)

        except Exception as e:
            print("[BLE] Error:", e)

        await asyncio.sleep(2)


# ========= BUTTON =========

def button_pressed():
    if not PRINT_ON_BUTTON:
        return

    if last_position is None:
        print("[BTN] No position yet")
        return

    x, y, z, q, ts = last_position
    age = time.time() - ts

    # Absolute values ONLY for display
    print(
        f"[BTN] x={abs(x):.3f} m, "
        f"y={abs(y):.3f} m, "
        f"z={abs(z):.3f} m, "
        f"q={q}, age={age:.2f}s"
    )


async def button_poll_loop():
    last_state = GPIO.input(BUTTON_PIN)

    while True:
        current = GPIO.input(BUTTON_PIN)

        if last_state == GPIO.LOW and current == GPIO.HIGH:
            button_pressed()
            await asyncio.sleep(0.25)  # debounce

        last_state = current
        await asyncio.sleep(0.02)


def setup_button():
    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)

    pull_cfg = GPIO.PUD_DOWN if GPIO_PULL == "DOWN" else GPIO.PUD_UP
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=pull_cfg)

    print(f"[GPIO] Button ready on GPIO{BUTTON_PIN} (pull {GPIO_PULL})")


# ========= MAIN =========

async def main_async():
    await asyncio.gather(
        ble_location_loop(),
        button_poll_loop(),
    )


def main():
    setup_button()
    try:
        asyncio.run(main_async())
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()

