import sys
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gio, Gtk
from views.main_view import MainView
from handlers.main_handler import MainHandler


class Application(Gtk.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="org.example.myapp",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs
        )
        self.window = None
        self.add_main_option(
            "test",
            ord("t"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "Command line test",
            None,
        )

    def do_startup(self):
        Gtk.Application.do_startup(self)
        menu_xml = ""
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.on_about)
        self.add_action(action)
        action = Gio.SimpleAction.new("quit", None)
        action.connect("activate", self.on_quit)
        self.add_action(action)
        with open("./ui/menu.xml", "r") as fs:
            menu_xml = fs.read()
            fs.close()
        builder = Gtk.Builder.new_from_string(menu_xml, -1)
        self.set_app_menu(builder.get_object("app-menu"))

    def do_activate(self):
        # We only allow a single window and raise any existing ones
        if not self.window:
            # Windows are associated with the application
            # when the last one is closed the application shuts down
            self.builder = Gtk.Builder()
            self.builder.add_from_file("./ui/MainView.glade")
            self.builder.connect_signals(MainHandler())
            # self.window = MainView(application=self, title="Main Window")
            self.window = self.builder.get_object("main-window")
            self.window.set_application(self)
        self.window.present()

    def do_command_line(self, command_line):
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "test" in options:
            # This is printed on the main instance
            print("Test argument recieved: %s" % options["test"])
        self.activate()
        return 0

    def on_about(self, *args):
        about_dialog = Gtk.AboutDialog(modal=True)
        about_dialog.present()

    def on_quit(self, *args):
        self.quit()