import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
from handlers.url_handler import UrlHandler
from views.url_view import UrlView
from views.proxy_view import ProxyView

class MainHandler:

    def __init__(self):
        self.builder = Gtk.Builder()

    def on_add_url_pressed(self, *args):
        url_dialog = UrlView()
        url_dialog.present()

    def add_proxy_pressed(self, *args):
        proxy_dialog = ProxyView()
        proxy_dialog.present()

    def on_kill_drive_pressed(self, *args):
        pass

    def on_settings_pressed(self, *args):
        pass