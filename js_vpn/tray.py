from __future__ import annotations

import gi

gi.require_version("AyatanaAppIndicator3", "0.1")
gi.require_version("Gtk", "3.0")

from gi.repository import AyatanaAppIndicator3, GLib, Gtk

from .vpn import disconnect, is_connected


class TrayIndicator:
    def __init__(self, window: Gtk.Window) -> None:
        self.window = window

        self.indicator = AyatanaAppIndicator3.Indicator.new(
            "vpn-js",
            "network-vpn-disconnected",
            AyatanaAppIndicator3.IndicatorCategory.APPLICATION_STATUS,
        )
        self.indicator.set_status(
            AyatanaAppIndicator3.IndicatorStatus.ACTIVE
        )

        self.status_item = Gtk.MenuItem(label="VPN desconectada")
        self.status_item.set_sensitive(False)

        menu = Gtk.Menu()
        menu.append(self.status_item)
        menu.append(Gtk.SeparatorMenuItem())

        open_item = Gtk.MenuItem(label="Abrir JS VPN")
        open_item.connect("activate", self.show_window)
        menu.append(open_item)

        disconnect_item = Gtk.MenuItem(label="Desconectar")
        disconnect_item.connect("activate", self.disconnect_vpn)
        menu.append(disconnect_item)
        self.disconnect_item = disconnect_item

        menu.append(Gtk.SeparatorMenuItem())

        quit_item = Gtk.MenuItem(label="Sair")
        quit_item.connect("activate", self.quit_application)
        menu.append(quit_item)

        menu.show_all()
        self.indicator.set_menu(menu)

        self.refresh_status()
        GLib.timeout_add_seconds(2, self.refresh_status)

    def show_window(self, _item=None) -> None:
        self.window.show_all()
        self.window.present()

    def disconnect_vpn(self, _item=None) -> None:
        disconnect()
        GLib.timeout_add_seconds(1, self.refresh_status)

    def quit_application(self, _item=None) -> None:
        Gtk.main_quit()

    def refresh_status(self) -> bool:
        connected = is_connected()

        if connected:
            self.indicator.set_icon_full(
                "network-vpn",
                "VPN conectada",
            )
            self.status_item.set_label("VPN conectada")
            self.disconnect_item.set_sensitive(True)
        else:
            self.indicator.set_icon_full(
                "network-vpn-disconnected",
                "VPN desconectada",
            )
            self.status_item.set_label("VPN desconectada")
            self.disconnect_item.set_sensitive(False)

        return True
