from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")

from gi.repository import GLib, Gtk

from .vpn import disconnect, is_connected


class TrayIndicator:
    def __init__(self, window: Gtk.Window) -> None:
        self.window = window

        self.tray_icon = Gtk.StatusIcon.new_from_icon_name(
            "network-vpn-disconnected"
        )
        self.tray_icon.set_tooltip_text("JS VPN")
        self.tray_icon.set_visible(True)

        self.menu = Gtk.Menu()

        self.status_item = Gtk.MenuItem(label="VPN desconectada")
        self.status_item.set_sensitive(False)
        self.menu.append(self.status_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        open_item = Gtk.MenuItem(label="Abrir JS VPN")
        open_item.connect("activate", self.show_window)
        self.menu.append(open_item)

        self.disconnect_item = Gtk.MenuItem(label="Desconectar")
        self.disconnect_item.connect("activate", self.disconnect_vpn)
        self.menu.append(self.disconnect_item)

        self.menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Sair")
        quit_item.connect("activate", self.quit_application)
        self.menu.append(quit_item)

        self.menu.show_all()

        # Clique esquerdo.
        self.tray_icon.connect("activate", self.show_window)

        # Clique direito.
        self.tray_icon.connect("popup-menu", self.show_context_menu)

        self.refresh_status()
        GLib.timeout_add_seconds(2, self.refresh_status)

    def show_context_menu(
        self,
        icon: Gtk.StatusIcon,
        button: int,
        activate_time: int,
    ) -> None:
        self.menu.popup(
            None,
            None,
            Gtk.StatusIcon.position_menu,
            icon,
            button,
            activate_time,
        )

    def show_window(self, _item=None) -> None:
        self.window.show_all()
        self.window.deiconify()
        self.window.present()

    def disconnect_vpn(self, _item=None) -> None:
        disconnect()
        GLib.timeout_add_seconds(1, self.refresh_status)

    def quit_application(self, _item=None) -> None:
        Gtk.main_quit()

    def refresh_status(self) -> bool:
        connected = is_connected()

        if connected:
            self.tray_icon.set_from_icon_name("network-vpn")
            self.tray_icon.set_tooltip_text("JS VPN — conectada")
            self.status_item.set_label("VPN conectada")
            self.disconnect_item.set_sensitive(True)
        else:
            self.tray_icon.set_from_icon_name(
                "network-vpn-disconnected"
            )
            self.tray_icon.set_tooltip_text("JS VPN — desconectada")
            self.status_item.set_label("VPN desconectada")
            self.disconnect_item.set_sensitive(False)

        return True