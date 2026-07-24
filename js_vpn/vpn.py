from __future__ import annotations

import subprocess
from pathlib import Path

GPSAML = Path.home() / ".local" / "bin" / "gp-saml-gui"
HIPREPORT = "/usr/libexec/openconnect/hipreport.sh"
OPENCONNECT = "/usr/sbin/openconnect"
KILLALL = "/usr/bin/killall"


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

    if not GPSAML.exists():
        raise FileNotFoundError(f"gp-saml-gui não encontrado em {GPSAML}")

    if not Path(OPENCONNECT).exists():
        raise FileNotFoundError(f"OpenConnect não encontrado em {OPENCONNECT}")

    command = f"""
echo 'Será aberta a tela de login Microsoft + MFA.'
echo

'{GPSAML}' \
    -S \
    --clientos=Linux \
    '{host}' \
    -- \
    --csd-wrapper='{HIPREPORT}' \
    --base-mtu=1200 \
    -b

RESULT=$?

if [ "$RESULT" -eq 0 ]; then
    zenity --info --title='JS VPN' --text='VPN conectada com sucesso.'
else
    zenity --error --title='JS VPN' --text="Falha ao conectar à VPN. Código: $RESULT"
fi

exit "$RESULT"
"""

    return subprocess.Popen(
        ["gnome-terminal", "--", "bash", "-c", command],
        start_new_session=True,
    )


def disconnect() -> bool:
    result = subprocess.run(
        ["sudo", KILLALL, "-SIGINT", "openconnect"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0
