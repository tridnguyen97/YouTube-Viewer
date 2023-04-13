import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
from utils.constants import PROXY_FILE_DIR


class ProxyView(Gtk.Dialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        main_layout = self.get_content_area()
        file_url_box = Gtk.Box(spacing=6)
        grid = Gtk.Grid()
       
        text_filter = Gtk.FileFilter()
        text_filter.set_name("Text files")
        text_filter.add_mime_type("text/*")
        all_filter = Gtk.FileFilter()
        all_filter.set_name("All files")
        all_filter.add_pattern("*")
       
        file_select_label = Gtk.Label(label="Import Proxy file")
        file_select_btn = Gtk.FileChooserButton("Import Proxy file")
        file_select_btn.add_filter(all_filter)
        file_select_btn.add_filter(text_filter)
        file_select_btn.connect("selection-changed", self.on_file_selected)
       
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_hexpand(True)
        scrolledwindow.set_vexpand(True)
        grid.attach(scrolledwindow, 0, 1, 3, 1)

        proxy_text = Gtk.TextView()
        self.proxy_text_buffer = proxy_text.get_buffer()
        scrolledwindow.add(proxy_text)
        file_url_box.pack_start(file_select_label, True, True, 0)
        file_url_box.pack_start(file_select_btn, True, True, 0)
        
        import_btn = Gtk.Button("Import")
        import_btn.connect("clicked", self.on_file_selected)
        self.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Import", Gtk.ResponseType.OK
        )

        main_layout.add(file_url_box)
        main_layout.add(grid)
        self.set_default_size(500, 300)
        self.show_all()

        response = self.run()
        if response == Gtk.ResponseType.OK:
            self.on_import_clicked()
        elif response == Gtk.ResponseType.CANCEL:
            self.destroy()

    def on_file_selected(self, widget):
        file_name = widget.get_filename()
        proxy_list = ""
        with open(file_name, "r") as f:
            proxy_list = f.read()
            f.close()
        self.proxy_text_buffer.set_text(proxy_list)

    def on_import_clicked(self, *args):
        iter_start = self.proxy_text_buffer.get_start_iter()
        iter_end = self.proxy_text_buffer.get_end_iter()
        proxy_list = self.proxy_text_buffer.get_text(iter_start, iter_end, False)
        with open(PROXY_FILE_DIR, "w") as fs:
            fs.write(proxy_list)
            fs.close()
            self.destroy()