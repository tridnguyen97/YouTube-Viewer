import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
from handlers.url_handler import UrlHandler
from views.url_view import UrlView

class MainHandler:

    def __init__(self):
        self.builder = Gtk.Builder()

    def on_add_url_pressed(self, *args):
        builder = Gtk.Builder()
        url_dialog = UrlView()
        url_dialog.present()

    def add_proxy_pressed(self, *args):
        proxy_dialog = self.builder.add_from_file("../ui/ProxyView.glade")
        window = proxy_dialog.get_object("proxy-view")
        window.show_all()

    def on_kill_drive_pressed(self, *args):
        pass

    def on_settings_pressed(self, *args):
        pass