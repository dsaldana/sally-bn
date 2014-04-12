
### Graphic widgets
from lib_sallybn import gwidgets

from gi.repository import Gtk

import sys

class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        # Graph
        vertices = ["A", "B", "C", "D"]
        edges = [["A", "B"], ["C", "B"], ["D", "B"]]

        states = {"A": ["atrue", "afalse"],
                  "B": ["true", "false"],
                  "C": ["ctrue", "cfalse"],
                  "D": ["1", "2", "3"]}

        cpt_v = "B"
        gtable = gwidgets.GraphicCptTable(vertices, edges, states, cpt_v)
        # table = gwidgets.create_treeview_for_cpt(vertices, edges, states, cpt_v)


        ## Window
        window = Gtk.Window(application=self, title="CPT for " + cpt_v)
        window.set_default_size(250, 100)
        window.set_border_width(10)

        # the label we use to show the selection
        label = Gtk.Label()
        label.set_text("fads")

        # a grid to attach the widgets
        grid = Gtk.Grid()
        grid.attach(gtable.get_widget(), 0, 0, 1, 1)
        grid.attach(label, 0, 1, 1, 1)

        # attach the grid to the window
        window.add(grid)
        window.show_all()

        if window:
            window.connect("destroy", Gtk.main_quit)

    def do_startup(self):
        Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)