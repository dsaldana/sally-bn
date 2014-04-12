
### Graphic widgets
from libsallydb import gwidgets

import libsallydb.gwidgets
from gi.repository import Gtk

import sys

class MyApplication(Gtk.Application):
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_activate(self):
        # Graph
        vertices = ["A", "B", "C"]
        edges = [["A", "B"], ["C", "B"]]
        states = {}
        states["A"] = ["atrue", "afalse"]
        states["B"] = ["true", "false"]
        states["C"] = ["ctrue", "afalse"]

        cpt_v = "B"
        win = gwidgets.CptTable(self, vertices, edges, states, cpt_v)
        win.show_all()

    def do_startup(self):
        Gtk.Application.do_startup(self)

app = MyApplication()
exit_status = app.run(sys.argv)
sys.exit(exit_status)