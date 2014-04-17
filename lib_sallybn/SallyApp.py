from gi.repository import Gtk

from lib_sallybn import WinHandler
# FIXME Not here
import lib_sallybn.util.resources as res


class SallyApp(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_startup(self):
        print "startup"
        Gtk.Application.do_startup(self)

    def do_activate(self):
        # Set the Glade file

        builder = Gtk.Builder()
        builder.add_from_file(res.MAIN_WINDOW_GLADE)

        #Get the Main Window, and connect the "destroy" event
        window = builder.get_object("MainWindow")
        window.set_size_request(800, 600)
        window.set_application(self)

        # Drawing area
        area = builder.get_object("drawingarea1")
        edit_buttons = [builder.get_object("bvertex"),
                        builder.get_object("bdelete"),
                        builder.get_object("bedge")]



        builder.connect_signals(WinHandler.WinHandler(window, area, edit_buttons))

        window.show_all()

        if window:
            window.connect("destroy", Gtk.main_quit)

