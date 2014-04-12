#!/usr/bin/env python


import sys
from lib_sallybn import SallyApp
from gi.repository import Gtk, Gdk
import math

from enum import Enum


# MAIN
if __name__ == "__main__":
    # hwg = Handler()
    # Gtk.main()
    app = SallyApp.SallyApp()
    exit_status = app.run(sys.argv)
    Gtk.main()
    sys.exit(exit_status)
