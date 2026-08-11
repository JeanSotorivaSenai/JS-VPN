from __future__ import annotations

import shutil
import sys
import subprocess
import tempfile
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = PROJECT_DIR / "js_vpn"

INSTALL_DIR = (
    Path.home()
    / ".local"
    / "share"
    / "vpn-js"
    / "js_vpn"
)

IGNORED_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".github",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
}


def update_sudoers() -> bool:
    """Atualiza as regras sudoers com as correções de segurança."""
    try:
        import os
        username = os.getenv("USER")
        if not username:
            print("Aviso: Não foi possível determinar o usuário atual.")
            return False

        sudoers_file = f"/etc/sudoers.d/vpn-js-{username}"

        # Verifica se o arquivo sudoers existe
        if not Path(sudoers_file).exists():
            print(f"Aviso: Arquivo sudoers não encontrado: {sudoers_file}")
            print("Execute a reinstalação completa: sudo ./installer/install.sh")
            return False

        # Encontra os caminhos dos executáveis
        result_openconnect = subprocess.run(["which", "openconnect"],
                                          capture_output=True, text=True)
        result_killall = subprocess.run(["which", "killall"],
                                      capture_output=True, text=True)

        if result_openconnect.returncode != 0 or result_killall.returncode != 0:
            print("Erro: openconnect ou killall não encontrados.")
            return False

        openconnect_path = result_openconnect.stdout.strip()
        killall_path = result_killall.stdout.strip()

        # Cria arquivo temporário com as novas regras
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.sudoers') as tmp:
            tmp.write(f"""# JS VPN - Regras restritivas para VPN
{username} ALL=(root) NOPASSWD: {openconnect_path} --csd-wrapper=/usr/libexec/openconnect/hipreport.sh --base-mtu=1200 -b *
{username} ALL=(root) NOPASSWD: {killall_path} -SIGINT openconnect
""")
            temp_file = tmp.name

        # Valida a sintaxe do arquivo sudoers
        result = subprocess.run(["sudo", "visudo", "-cf", temp_file],
                              capture_output=True, text=True)

        if result.returncode != 0:
            Path(temp_file).unlink(missing_ok=True)
            print(f"Erro na validação do sudoers: {result.stderr}")
            return False

        # Instala o novo arquivo sudoers
        result = subprocess.run([
            "sudo", "install", "-o", "root", "-g", "root", "-m", "0440",
            temp_file, sudoers_file
        ], capture_output=True, text=True)

        # Remove arquivo temporário
        Path(temp_file).unlink(missing_ok=True)

        if result.returncode == 0:
            print("✅ Regras sudoers atualizadas com correções de segurança.")
            return True
        else:
            print(f"Erro ao atualizar sudoers: {result.stderr}")
            return False

    except Exception as e:
        print(f"Erro ao atualizar sudoers: {e}")
        return False


def ignore_files(
    directory: str,
    names: list[str],
) -> set[str]:
    return {
        name
        for name in names
        if name in IGNORED_NAMES
        or name.endswith(".pyc")
        or name.endswith(".pyo")
    }


def install_application() -> None:
    if not SOURCE_DIR.exists():
        raise RuntimeError(
            f"Pasta do projeto não encontrada: {SOURCE_DIR}"
        )

    INSTALL_DIR.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_dir = INSTALL_DIR.with_name("js_vpn.new")
    backup_dir = INSTALL_DIR.with_name("js_vpn.backup")

    if temporary_dir.exists():
        shutil.rmtree(temporary_dir)

    print(f"Copiando arquivos de:\n{SOURCE_DIR}")
    print(f"\nPara:\n{INSTALL_DIR}")

    shutil.copytree(
        SOURCE_DIR,
        temporary_dir,
        ignore=ignore_files,
    )

    if backup_dir.exists():
        shutil.rmtree(backup_dir)

    if INSTALL_DIR.exists():
        INSTALL_DIR.rename(backup_dir)

    try:
        temporary_dir.rename(INSTALL_DIR)
    except Exception:
        if INSTALL_DIR.exists():
            shutil.rmtree(INSTALL_DIR)

        if backup_dir.exists():
            backup_dir.rename(INSTALL_DIR)

        raise
    else:
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
    
    print("✅ Arquivos Python atualizados com sucesso.")


def wait_before_closing() -> None:
    if sys.stdin.isatty():
        input("\nPressione Enter para fechar...")


def main() -> int:
    try:
        # Atualiza os arquivos Python
        install_application()
        
        # Tenta atualizar as regras sudoers (precisa de sudo)
        print("\n🔒 Atualizando regras de segurança...")
        sudoers_updated = update_sudoers()
        
        if not sudoers_updated:
            print("\n⚠️  Aviso: Regras sudoers não foram atualizadas.")
            print("Para aplicar todas as correções de segurança, execute:")
            print("sudo ./installer/install.sh")
        
    except Exception as error:
        print(f"\nErro durante a atualização:\n{error}")
        wait_before_closing()
        return 1

    print("\n✅ JS VPN atualizado com sucesso.")
    if sudoers_updated:
        print("🛡️  Correções de segurança aplicadas.")
    
    wait_before_closing()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())