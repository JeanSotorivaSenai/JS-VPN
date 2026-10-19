from __future__ import annotations

import argparse
import re
import shlex
import subprocess
from pathlib import Path
from urllib.parse import urlsplit


GPSAML = Path.home() / ".local" / "bin" / "gp-saml-gui"
HIPREPORT = "/usr/libexec/openconnect/hipreport.sh"
OPENCONNECT = "/usr/sbin/openconnect"
HOST_PATTERN = r"[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?"


def parse_saml_output(output: str, interface: str) -> dict[str, str]:
    # gp-saml-gui emits shell-quoted assignments; parse them without a shell.
    values = {}
    for assignment in shlex.split(output):
        key, separator, value = assignment.partition("=")
        if not separator or key not in {"HOST", "USER", "COOKIE", "OS"} or key in values:
            raise ValueError("Resposta SAML invalida.")
        values[key] = value

    if set(values) != {"HOST", "USER", "COOKIE", "OS"}:
        raise ValueError("Resposta SAML incompleta.")
    if any(not value or any(char in value for char in "\r\n\0") for value in values.values()):
        raise ValueError("Resposta SAML invalida.")

    endpoint = urlsplit(values["HOST"])
    if (
        endpoint.scheme != "https"
        or not endpoint.hostname
        or endpoint.username is not None
        or endpoint.password is not None
        or endpoint.query
        or endpoint.fragment
        or endpoint.path not in {
            f"/{interface}:prelogin-cookie",
            f"/{interface}:portal-userauthcookie",
        }
    ):
        raise ValueError("Destino SAML invalido.")
    if values["OS"] not in {"linux-64", "win", "mac-intel"}:
        raise ValueError("Sistema operacional SAML invalido.")

    return values


def authenticate(host: str, interface: str = "gateway", clientos: str = "Linux") -> int:
    if not re.fullmatch(HOST_PATTERN, host):
        raise ValueError("Host da VPN invalido.")
    if interface not in {"gateway", "portal"} or clientos not in {"Linux", "Windows", "Mac"}:
        raise ValueError("Opcao de autenticacao invalida.")

    print("Sera aberta a tela de login Microsoft + MFA.", flush=True)
    saml = subprocess.run(
        [str(GPSAML), "-q", f"--{interface}", f"--clientos={clientos}", host],
        stdout=subprocess.PIPE,
        text=True,
        check=False,
    )
    if saml.returncode != 0:
        return saml.returncode

    values = parse_saml_output(saml.stdout, interface)
    endpoint = urlsplit(values["HOST"])
    # Keep the fixed options first to match the existing sudoers rule.
    command = [
        "sudo",
        OPENCONNECT,
        f"--csd-wrapper={HIPREPORT}",
        "--base-mtu=1200",
        "-b",
        "--protocol=gp",
        f"--user={values['USER']}",
        f"--os={values['OS']}",
        f"--usergroup={endpoint.path.lstrip('/')}",
        "--passwd-on-stdin",
        f"https://{endpoint.netloc}",
    ]
    result = subprocess.run(
        command,
        input=values["COOKIE"] + "\n",
        text=True,
        check=False,
    )
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Autenticacao SAML da JS VPN.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--gateway", dest="interface", action="store_const", const="gateway")
    mode.add_argument("--portal", dest="interface", action="store_const", const="portal")
    parser.set_defaults(interface="gateway")
    parser.add_argument("--clientos", choices=("Linux", "Windows", "Mac"), default="Linux")
    parser.add_argument("host")
    args = parser.parse_args(argv)

    try:
        result = authenticate(args.host, args.interface, args.clientos)
    except (OSError, ValueError):
        print("Falha ao iniciar a conexao ou resposta SAML invalida.", flush=True)
        result = 1

    success = result == 0
    message = "VPN conectada com sucesso." if success else f"Falha ao conectar a VPN. Codigo: {result}"
    subprocess.run(
        ["zenity", "--info" if success else "--error", "--title=JS VPN", f"--text={message}"],
        check=False,
    )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
