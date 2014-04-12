from gi.repository import Gtk
from lib_sallybn import drawing_area


class SallyApp(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_startup(self):
        print "startup"
        Gtk.Application.do_startup(self)

    def do_activate(self):
        # Set the Glade file
        glade_file = 'visual_editor.glade'

        builder = Gtk.Builder()
        builder.add_from_file(glade_file)

        #Get the Main Window, and connect the "destroy" event
        window = builder.get_object("MainWindow")
        window.set_size_request(800, 600)
        window.set_application(self)

        # Drawing area
        area = builder.get_object("drawingarea1")
        builder.connect_signals(drawing_area.Handler(area))

        window.show_all()
        if window:
            window.connect("destroy", Gtk.main_quit)