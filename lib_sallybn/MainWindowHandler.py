from gi.repository import Gtk

from lib_sallybn.disc_bayes_net.BoxDiscreteBN import BoxDiscreteBN



## Class
class MainWindowHandler:
    def __init__(self, window, tabber):
        self.window = window
        self.tabber = tabber

        self.tab_bn = BoxDiscreteBN(window)
        self.tabber.append_page(self.tab_bn.get_box(),
                                Gtk.Label("New"))

    def on_save(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_parent(self.window)
        dialog.set_modal(True)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Sally files")
        filter_py.add_pattern("*" + BoxDiscreteBN.FILE_EXTENSION)
        dialog.add_filter(filter_py)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            #self.save_bn_to_file(self.disc_bn, self.vertex_locations, dialog.get_filename())
            #TODO send tab to save
            pass

        dialog.destroy()


    def on_open(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK),
                                       flags=Gtk.DialogFlags.MODAL)

        # dialog.set_transient_for(self.window)
        # self.window.set_transient_for(dialog)
        dialog.set_parent(self.window)
        dialog.set_modal(True)
        # Filter
        filter_py = Gtk.FileFilter()
        filter_py.set_name("Sally files")
        filter_py.add_pattern("*" + BoxDiscreteBN.FILE_EXTENSION)
        dialog.add_filter(filter_py)

        #RUN
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("File selected: " + dialog.get_filename())
            # TODO create new tab
            #self.disc_bn, self.vertex_locations = self.load_bn_from_file(dialog.get_filename())
            #self.win_discbn.disc_bn = self.disc_bn
            # TODO create an alg to show the nodes if vertex locations does not exist

        dialog.destroy()

    def on_new(self, widget):
        print "new"
        self.tab_bn = BoxDiscreteBN(self.window)
        self.tabber.append_page(self.tab_bn.get_box(),
                                Gtk.Label("New"))