# ----------------------------------------------------------------------------
#
# Sally BN: An Open-Source Framework for Bayesian Networks.
#
# Copyright (C) 2014  David Saldana (dajulian@gmail.com)
#
# ----------------------------------------------------------------------------
# GNU General Public License v2
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# ----------------------------------------------------------------------------

from gi.repository import Gtk

from lib_sallybn import MainWindowHandler
# FIXME Not here
import lib_sallybn.util.resources as res
from lib_sallybn.util.splash import show_splash


class SallyApp(Gtk.Application):
    """
    GTK Application.
    """
    def __init__(self):
        Gtk.Application.__init__(self)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_activate(self):
        # Set the Glade file
        builder = Gtk.Builder()
        builder.add_from_file(res.MAIN_WINDOW_GLADE)

        try:
            show_splash()
        except:
            print "Not splash"
        #Get the Main Window, and connect the "destroy" event
        window = builder.get_object("MainWindow")
        window.set_size_request(800, 600)
        window.set_application(self)

        #notebook_main
        tabber = builder.get_object("notebook_main")
        tabber.remove_page(0)

        # Handler for signals generated by main window
        handler = MainWindowHandler.MainWindowHandler(window, tabber)
        builder.connect_signals(handler)

        window.connect("delete-event", Gtk.main_quit)
        window.connect("destroy", Gtk.main_quit)

        window.show_all()




