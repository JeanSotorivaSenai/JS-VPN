from __future__ import annotations

import subprocess
import re
import sys
from pathlib import Path

from .auth import GPSAML, HOST_PATTERN, OPENCONNECT
from .dns_manager import DNSManager

KILLALL = "/usr/bin/killall"

# Instância global do gerenciador DNS
dns_manager = DNSManager()


def is_connected() -> bool:
    result = subprocess.run(
        ["pgrep", "-x", "openconnect"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def connect(host: str) -> subprocess.Popen:
    host = host.strip()

    if not host:
        raise ValueError("Informe o host da VPN.")

    # Valida o formato do host para prevenir command injection
    if not re.fullmatch(HOST_PATTERN, host):
        raise ValueError("Host da VPN contém caracteres inválidos.")

    if not GPSAML.exists():
        raise FileNotFoundError(f"gp-saml-gui não encontrado em {GPSAML}")

    if not Path(OPENCONNECT).exists():
        raise FileNotFoundError(f"OpenConnect não encontrado em {OPENCONNECT}")

    # Faz backup do DNS antes da conexão
    dns_manager.backup_dns()

    return subprocess.Popen(
        [
            "gnome-terminal",
            f"--working-directory={Path(__file__).resolve().parent.parent}",
            "--",
            sys.executable,
            "-m",
            "js_vpn.auth",
            host,
        ],
        start_new_session=True,
    )


def disconnect() -> bool:
    result = subprocess.run(
        ["sudo", KILLALL, "-SIGINT", "openconnect"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    
    # Restaura o DNS após desconectar
    if result.returncode == 0:
        dns_manager.restore_dns()
    
    return result.returncode == 0


def check_dns_status() -> dict[str, any]:
    """Retorna informações sobre o status do DNS."""
    return {
        "modified": dns_manager.is_dns_modified(),
        "servers": dns_manager.get_current_dns_servers(),
    }
