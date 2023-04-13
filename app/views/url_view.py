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
        text_filter = Gtk.FileFilter()
        text_filter.set_name("Text files")
        text_filter.add_mime_type("text/*")
        all_filter = Gtk.FileFilter()
        all_filter.set_name("All files")
        all_filter.add_pattern("*")
        
        file_import_label = Gtk.Label(label="Import URL file")
        file_import_btn = Gtk.FileChooserButton("Import URL file")
        file_import_btn.add_filter(text_filter)
        file_import_btn.add_filter(all_filter)
        file_import_btn.connect("selection-changed", self.on_file_selected)
        file_url_box.pack_start(file_import_label, True, True, 0)
        file_url_box.pack_start(file_import_btn, True, True, 0)
        main_layout.add(file_url_box)
        self.set_default_size(500, 300)
        self.show_all()

    def on_file_selected(self, *args):
        pass