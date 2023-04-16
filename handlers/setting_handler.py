import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk


class SettingHandler:

    def on_database_toggled(self, *args):
        pass

    def on_http_toggled(self, *args):
        pass

    def on_proxy_manual_toggled(self, *args):
        pass
