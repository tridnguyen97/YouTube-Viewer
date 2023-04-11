import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk


class UrlView(Gtk.Dialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        main_layout = self.get_content_area()
        file_url_box = Gtk.Box(spacing=6)

        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK
        )
        file_import_btn = Gtk.Button("Import URL file")
        file_import_btn.connect("clicked", self.on_import_clicked)
        file_url_box.pack_start(file_import_btn, True, True, 0)
        main_layout.add(file_url_box)
        self.set_default_size(500, 300)
        self.show_all()

    def on_import_clicked(self, *args):
        pass