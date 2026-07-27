from __future__ import annotations

import shutil
import sys
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


def wait_before_closing() -> None:
    if sys.stdin.isatty():
        input("\nPressione Enter para fechar...")


def main() -> int:
    try:
        install_application()
    except Exception as error:
        print(f"\nErro durante a atualização:\n{error}")
        wait_before_closing()
        return 1

    print("\nJS VPN atualizado com sucesso.")
    wait_before_closing()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())