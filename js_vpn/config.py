from __future__ import annotations

import configparser
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "vpn-js"
CONFIG_FILE = CONFIG_DIR / "config.ini"


def load_host() -> str:
    config = configparser.ConfigParser()
    if not CONFIG_FILE.exists():
        return ""
    config.read(CONFIG_FILE, encoding="utf-8")
    return config.get("VPN", "host", fallback="").strip()


def save_host(host: str) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    config = configparser.ConfigParser()
    config["VPN"] = {"host": host.strip()}
    with CONFIG_FILE.open("w", encoding="utf-8") as file:
        config.write(file)
