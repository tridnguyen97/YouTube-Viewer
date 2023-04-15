import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from handlers.setting_handler import SettingHandler


class SettingView(Gtk.Dialog):

    def __init__(self,  *args, **kwargs):
        Gtk.Dialog.__init__(self, *args, **kwargs)
        builder = Gtk.Builder()
        builder.add_from_file("./ui/SettingView.glade")
        builder.connect_signals(SettingHandler())
        self.dialog = builder.get_object("setting-view")
        apply_btn = Gtk.Button(label="Apply")
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Apply", Gtk.ResponseType.OK
        )
        self.get_content_area().add(self.dialog)
        self.set_default_size(500, 300)
