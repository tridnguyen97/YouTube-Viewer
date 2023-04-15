import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
from views.setting_view import SettingView
from views.url_view import UrlView
from views.proxy_view import ProxyView
from youtubeviewer.config import create_config

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
        setting_dialog = SettingView()
        response = setting_dialog.run()
        if response == Gtk.ResponseType.OK:
            print("OK button clicked")
            print(setting_dialog.__dict__)
        else:
            print("Dialog closed")

        setting_dialog.destroy()