from gi.repository import Gtk

from lib_sallybn.disc_bayes_net.BoxDiscreteBN import BoxDiscreteBN, FILE_EXTENSION
import ntpath


## Class
class MainWindowHandler:
    def __init__(self, window, tabber):
        self.window = window
        self.tabber = tabber
        # Add a clean bn
        self.add_bn_tab("New Bayesian Network")

    def on_save(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))
        dialog.set_parent(self.window)
        dialog.set_modal(True)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Sally files")
        filter_py.add_pattern("*" + FILE_EXTENSION)
        dialog.add_filter(filter_py)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            # get selected tab
            n_tab = self.tabber.get_current_page()
            disc_bn = self.tabber.get_nth_page(n_tab)
            # save
            disc_bn.save_bn_to_file(dialog.get_filename())

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
        filter_py.add_pattern("*" + FILE_EXTENSION)
        dialog.add_filter(filter_py)

        #RUN
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            file_name = ntpath.basename(file_path)
            file_name= file_name.replace(FILE_EXTENSION, "")

            # Create and add the tab
            tab_bn = self.add_bn_tab(file_name)
            # Load from file
            tab_bn.load_bn_from_file(file_path)

            #TODO validate if the bn is good
            self.goto_last_tab()

        dialog.destroy()

    def on_new(self, widget):
        print "new"
        self.add_bn_tab("New BN")


    def add_bn_tab(self, title):
        tab_bn = BoxDiscreteBN(self.window)
        self.tabber.append_page(tab_bn,
                                Gtk.Label(title))
        self.goto_last_tab()
        return tab_bn

    def goto_last_tab(self):
        # select loaded tab
        n_new_tab = self.tabber.get_n_pages()
        self.tabber.set_current_page(n_new_tab - 1)
