from __future__ import annotations

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional

RESOLV_CONF = Path("/etc/resolv.conf")
BACKUP_SUFFIX = ".vpn-backup"


class DNSManager:
    """Gerencia o DNS durante conexões VPN para evitar problemas após reboot."""

    def __init__(self):
        self.backup_file = Path(f"{RESOLV_CONF}{BACKUP_SUFFIX}")

    def backup_dns(self) -> bool:
        """Faz backup do resolv.conf atual."""
        try:
            if RESOLV_CONF.exists() and not self.backup_file.exists():
                shutil.copy2(RESOLV_CONF, self.backup_file)
                return True
        except (OSError, PermissionError) as e:
            print(f"Aviso: Não foi possível fazer backup do DNS: {e}")
        return False

    def restore_dns(self) -> bool:
        """Restaura o DNS original se houver backup."""
        try:
            if self.backup_file.exists():
                # Usa sudo para restaurar o arquivo
                result = subprocess.run([
                    "sudo", "cp", str(self.backup_file), str(RESOLV_CONF)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    # Remove o backup após restaurar
                    subprocess.run(["sudo", "rm", str(self.backup_file)],
                                 capture_output=True)
                    return True
        except (OSError, subprocess.SubprocessError) as e:
            print(f"Aviso: Não foi possível restaurar o DNS: {e}")
        return False

    def is_dns_modified(self) -> bool:
        """Verifica se o DNS foi modificado pela VPN."""
        return self.backup_file.exists()

    def get_current_dns_servers(self) -> list[str]:
        """Retorna lista dos servidores DNS atuais."""
        dns_servers = []
        try:
            if RESOLV_CONF.exists():
                content = RESOLV_CONF.read_text()
                for line in content.split('\n'):
                    line = line.strip()
                    if line.startswith('nameserver '):
                        dns_server = line.split()[1]
                        dns_servers.append(dns_server)
        except (OSError, IndexError):
            pass
        return dns_servers