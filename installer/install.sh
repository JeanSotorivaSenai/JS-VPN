#!/usr/bin/env bash

set -euo pipefail

APP_NAME="JS VPN"
APP_ID="vpn-js"

if [[ $EUID -ne 0 ]]; then
    echo "Execute com: sudo ./installer/install.sh"
    exit 1
fi

if [[ -z "${SUDO_USER:-}" || "$SUDO_USER" == "root" ]]; then
    echo "Não foi possível identificar o usuário comum."
    exit 1
fi

USERNAME="$SUDO_USER"
USER_HOME="$(getent passwd "$USERNAME" | cut -d: -f6)"
USER_GROUP="$(id -gn "$USERNAME")"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

INSTALL_DIR="$USER_HOME/.local/share/vpn-js"
APPLICATIONS_DIR="$USER_HOME/.local/share/applications"
AUTOSTART_DIR="$USER_HOME/.config/autostart"

apt-get update
apt-get install -y \
    openconnect \
    gnome-terminal \
    python3 \
    zenity \
    python3-pip \
    python3-gi \
    gir1.2-gtk-3.0 \
    gir1.2-webkit2-4.1 \
    gir1.2-ayatanaappindicator3-0 \
    libayatana-appindicator3-1 \
    psmisc \
    desktop-file-utils \
    git

GPSAML="$USER_HOME/.local/bin/gp-saml-gui"

if [[ ! -x "$GPSAML" ]]; then
    PIP_ARGS=(
        --user
    )

    if python3 -m pip install --help 2>&1 | grep -q -- '--break-system-packages'; then
        PIP_ARGS+=(--break-system-packages)
    fi

    sudo -u "$USERNAME" \
        HOME="$USER_HOME" \
        python3 -m pip install \
            "${PIP_ARGS[@]}" \
            'git+https://github.com/dlenski/gp-saml-gui.git'
fi

if [[ ! -x "$GPSAML" ]]; then
    echo "Erro: gp-saml-gui não foi instalado corretamente em:"
    echo "$GPSAML"
    exit 1
fi

install -d -o "$USERNAME" -g "$USER_GROUP" -m 0755 "$INSTALL_DIR"
rm -rf "$INSTALL_DIR/js_vpn"
cp -R "$PROJECT_DIR/js_vpn" "$INSTALL_DIR/js_vpn"

chown -R "$USERNAME:$USER_GROUP" "$INSTALL_DIR"
find "$INSTALL_DIR" -type d -exec chmod 0755 {} \;
find "$INSTALL_DIR" -type f -exec chmod 0644 {} \;
chmod 0755 "$INSTALL_DIR/js_vpn/main.py"

OPENCONNECT_PATH="$(command -v openconnect || true)"
KILLALL_PATH="$(command -v killall || true)"

if [[ -z "$OPENCONNECT_PATH" ]]; then
    echo "Erro: openconnect não foi encontrado."
    exit 1
fi

if [[ -z "$KILLALL_PATH" ]]; then
    echo "Erro: killall não foi encontrado."
    exit 1
fi

SUDOERS_FILE="/etc/sudoers.d/${APP_ID}-${USERNAME}"
TEMP_FILE="$(mktemp)"

cat > "$TEMP_FILE" <<EOF
${USERNAME} ALL=(root) NOPASSWD: ${OPENCONNECT_PATH} *
${USERNAME} ALL=(root) NOPASSWD: ${KILLALL_PATH} -SIGINT openconnect
EOF

chmod 0440 "$TEMP_FILE"
visudo -cf "$TEMP_FILE"
install -o root -g root -m 0440 "$TEMP_FILE" "$SUDOERS_FILE"
rm -f "$TEMP_FILE"

install -d -o "$USERNAME" -g "$USER_GROUP" -m 0755 "$APPLICATIONS_DIR"

cat > "$APPLICATIONS_DIR/${APP_ID}.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Comment=Conectar e desconectar a VPN
Exec=sh -c 'cd "${INSTALL_DIR}" && exec python3 -m js_vpn.main'
Icon=network-vpn
Terminal=false
Categories=Network;
StartupNotify=true
EOF

chown "$USERNAME:$USER_GROUP" "$APPLICATIONS_DIR/${APP_ID}.desktop"
chmod 0755 "$APPLICATIONS_DIR/${APP_ID}.desktop"

install -d -o "$USERNAME" -g "$USER_GROUP" -m 0755 "$AUTOSTART_DIR"

cat > "$AUTOSTART_DIR/${APP_ID}.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=${APP_NAME}
Comment=Iniciar o indicador da JS VPN
Exec=sh -c 'cd "${INSTALL_DIR}" && exec python3 -m js_vpn.main'
Icon=network-vpn
Terminal=false
X-GNOME-Autostart-enabled=true
StartupNotify=false
EOF

chown "$USERNAME:$USER_GROUP" "$AUTOSTART_DIR/${APP_ID}.desktop"
chmod 0644 "$AUTOSTART_DIR/${APP_ID}.desktop"

update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true

echo
echo "Instalação concluída."
echo "Abra o menu de aplicativos e pesquise por: ${APP_NAME}"
