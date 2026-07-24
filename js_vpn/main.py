#!/usr/bin/env python3

import signal
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from js_vpn.tray import TrayIndicator
from js_vpn.ui import MainWindow
from gi.repository import Gtk, GLib

GLib.set_prgname("vpn-js")
GLib.set_application_name("JS VPN")

def main() -> None:
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    window = MainWindow()

    # Fechar a janela apenas oculta o app; o ícone continua na bandeja.
    window.connect("delete-event", lambda *_args: (window.hide(), True)[1])

    TrayIndicator(window)

    window.show_all()
    Gtk.main()


if __name__ == "__main__":
    main()
