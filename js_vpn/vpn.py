from __future__ import annotations

import subprocess
import shlex
from pathlib import Path

from .dns_manager import DNSManager

GPSAML = Path.home() / ".local" / "bin" / "gp-saml-gui"
HIPREPORT = "/usr/libexec/openconnect/hipreport.sh"
OPENCONNECT = "/usr/sbin/openconnect"
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
    import re
    if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$', host):
        raise ValueError("Host da VPN contém caracteres inválidos.")

    if not GPSAML.exists():
        raise FileNotFoundError(f"gp-saml-gui não encontrado em {GPSAML}")

    if not Path(OPENCONNECT).exists():
        raise FileNotFoundError(f"OpenConnect não encontrado em {OPENCONNECT}")

    # Faz backup do DNS antes da conexão
    dns_manager.backup_dns()

    # Usa lista de argumentos em vez de string interpolada para evitar injection
    command = [
        "bash", "-c", f"""
echo 'Será aberta a tela de login Microsoft + MFA.'
echo

{shlex.quote(str(GPSAML))} \\
    -S \\
    --clientos=Linux \\
    {shlex.quote(host)} \\
    -- \\
    --csd-wrapper={shlex.quote(HIPREPORT)} \\
    --base-mtu=1200 \\
    -b

RESULT=$?

if [ "$RESULT" -eq 0 ]; then
    zenity --info --title='JS VPN' --text='VPN conectada com sucesso.'
else
    zenity --error --title='JS VPN' --text="Falha ao conectar à VPN. Código: $RESULT"
fi

exit "$RESULT"
"""
    ]

    return subprocess.Popen(
        ["gnome-terminal", "--"] + command,
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
