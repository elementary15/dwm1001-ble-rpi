import yaml
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config():
    if not CONFIG_PATH.exists():
        print(f"[CONFIG] Missing config.yaml at {CONFIG_PATH}")
        sys.exit(1)

    try:
        with open(CONFIG_PATH, "r") as f:
            cfg = yaml.safe_load(f)
    except Exception as e:
        print("[CONFIG] Failed to read config.yaml:", e)
        sys.exit(1)

    # ---- VALIDATION ----
    try:
        ble = cfg["ble"]
        gpio = cfg["gpio"]

        dwm_mac = ble["dwm_mac"]
        location_mode = int(ble.get("location_mode", 2))

        button_pin = int(gpio["button_pin"])
        pull = gpio.get("pull", "DOWN").upper()

        if pull not in ("UP", "DOWN"):
            raise ValueError("gpio.pull must be UP or DOWN")

    except Exception as e:
        print("[CONFIG] Invalid config.yaml structure:", e)
        sys.exit(1)

    return {
        "ble": {
            "dwm_mac": dwm_mac,
            "location_mode": location_mode,
        },
        "gpio": {
            "button_pin": button_pin,
            "pull": pull,
        },
        "logging": cfg.get("logging", {}),
    }


CONFIG = load_config()

