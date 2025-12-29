DWM1001 BLE Position Logger for Raspberry Pi
A configurable Python application that reads real-time position data from a Decawave DWM1001 tag over Bluetooth Low Energy (BLE) and logs coordinates upon a physical button press.

📌 Project Overview
Most DWM1001 scripts rely on hardcoded MAC addresses and GPIO pins. This project adopts a "configuration-first" approach, separating core logic from hardware specifics. This ensures that moving to a different Raspberry Pi or swapping tags requires zero code changes.

Key Features

Decoupled Logic: Hardware settings are managed via config.yaml.

Robust BLE Handling: Automatic reconnection if the BLE signal drops.

Validation: config_loader.py performs strict validation to prevent silent failures.

Hardware Friendly: Minimal overhead, designed for reliable GPIO polling.

🛠 Hardware Requirements
Raspberry Pi (Pi 3, 4, or Zero 2 W recommended)

DWM1001 Tag (with BLE firmware enabled)

Momentary Push Button



🏗 Initial Hardware Setup
Before running the Python application, the DWM1001 boards must be flashed with the correct firmware and configured as tags.

1. Flash Firmware

Download and install SEGGER J-Flash Lite.

Connect your DWM1001-DEV board via USB.

Select the device nRF52832_xxAA.

Load the DWM1001 firmware .hex file and click Program Device.

2. Configure as Tags

Use a serial terminal (like Minicom) to set the device mode:

Open Minicom: minicom -D /dev/ttyACM0 (on Linux) or use PuTTY (on Windows).

Press Enter twice to access the shell.

Use the command nmt to configure the node as a Tag.
Use the command nma to configure the node as an Anchor.

Enable BLE using the command nbe.

Type acts to verify the node is receiving position data from your anchor network.

🚀 Installation
Clone the repository:

Bash
git clone https://github.com/elementary15/dwm1001-ble-logger.git
cd dwm1001-ble-logger

Bash
sudo raspi-config

Install Dependencies:
Bash
pip install -r requirements.txt

⚙️ Configuration
All customization is handled in config.yaml. You do not need to edit any Python files.

YAML
# Example config.yaml structure
device:
  mac_address: "AA:BB:CC:DD:EE:FF"
  location_mode: "active"

gpio:
  button_pin: 17
  pull_mode: "up" # or "down"
  print_on_press: true
  
📋 How It Works
Initialization: The app loads config.yaml and validates the MAC address and GPIO pin range.

BLE Task: Connects to the DWM1001 and subscribes to position notifications. Coordinates (X, Y, Z in meters) are cached in memory.

GPIO Task: Monitors the physical button state.

Logging: When the button is pressed, the latest cached coordinates are printed to the console.

🏃 Running the Application
Since the script requires access to the GPIO pins, it must be run with sudo:

Bash
sudo python3 main.py


