from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

from .config import load_host, save_host
from .vpn import connect, disconnect, is_connected


class MainWindow(Gtk.Window):
    def __init__(self) -> None:
        super().__init__(title="JS VPN")
        self.set_default_size(440, 240)
        self.set_resizable(False)
        self.set_border_width(20)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.add(box)

        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold'>JS VPN</span>")
        title.set_xalign(0)
        box.pack_start(title, False, False, 0)

        host_label = Gtk.Label(label="Host da VPN")
        host_label.set_xalign(0)
        box.pack_start(host_label, False, False, 0)

        self.host_entry = Gtk.Entry()
        self.host_entry.set_placeholder_text("vpn-guest.exemplo.com.br")
        self.host_entry.set_text(load_host())
        box.pack_start(self.host_entry, False, False, 0)

        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        box.pack_start(self.status_label, False, False, 0)

        buttons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.pack_start(buttons, False, False, 0)

        self.connect_button = Gtk.Button(label="Conectar")
        self.connect_button.connect("clicked", self.on_connect)
        buttons.pack_start(self.connect_button, True, True, 0)

        self.disconnect_button = Gtk.Button(label="Desconectar")
        self.disconnect_button.connect("clicked", self.on_disconnect)
        buttons.pack_start(self.disconnect_button, True, True, 0)

        self.refresh_status()
        GLib.timeout_add_seconds(2, self.refresh_status)

    def show_message(self, message_type, title: str, text: str) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            flags=0,
            message_type=message_type,
            buttons=Gtk.ButtonsType.OK,
            text=title,
        )
        dialog.format_secondary_text(text)
        dialog.run()
        dialog.destroy()

    def on_connect(self, _button) -> None:
        host = self.host_entry.get_text().strip()

        if not host:
            self.show_message(
                Gtk.MessageType.WARNING,
                "Host não informado",
                "Informe o endereço da VPN antes de conectar.",
            )
            return

        # Valida o formato do host antes de prosseguir
        import re
        if not re.match(r'^[a-zA-Z0-9]([a-zA-Z0-9\-\.]*[a-zA-Z0-9])?$', host):
            self.show_message(
                Gtk.MessageType.ERROR,
                "Host inválido",
                "O host da VPN contém caracteres inválidos. Use apenas letras, números, pontos e hífens.",
            )
            return

        save_host(host)

        try:
            self.status_label.set_markup(
                "<b>Status:</b> <span foreground='#b26a00'>Conectando...</span>"
            )
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(False)
            self.host_entry.set_sensitive(False)
            connect(host)
        except (ValueError, FileNotFoundError, OSError) as error:
            self.show_message(
                Gtk.MessageType.ERROR,
                "Não foi possível iniciar a conexão",
                str(error),
            )
            self.refresh_status()

    def on_disconnect(self, _button) -> None:
        if not disconnect():
            self.show_message(
                Gtk.MessageType.ERROR,
                "Falha ao desconectar",
                "Não foi possível encerrar o OpenConnect.",
            )
        GLib.timeout_add_seconds(1, self.refresh_status)

    def refresh_status(self) -> bool:
        connected = is_connected()

        if connected:
            self.status_label.set_markup(
                "<b>Status:</b> <span foreground='#138a36'>Conectada</span>"
            )
            self.connect_button.set_sensitive(False)
            self.disconnect_button.set_sensitive(True)
            self.host_entry.set_sensitive(False)
        else:
            self.status_label.set_markup(
                "<b>Status:</b> <span foreground='#a12a2a'>Desconectada</span>"
            )
            self.connect_button.set_sensitive(True)
            self.disconnect_button.set_sensitive(False)
            self.host_entry.set_sensitive(True)

        return True
