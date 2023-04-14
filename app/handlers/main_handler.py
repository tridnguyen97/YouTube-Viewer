import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
from handlers.setting_handler import SettingHandler
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
        builder = Gtk.Builder()
        builder.add_from_file("./ui/SettingView.glade")
        builder.connect_signals(SettingHandler())
        window = builder.get_object("setting-view")
        window.show_all()