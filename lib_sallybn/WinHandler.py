from gi.repository import Gtk, Gdk
import math

from enum import Enum

from lib_sallybn.DiscreteBayesianNetworkExt import DiscreteBayesianNetworkExt
from lib_sallybn.WinDiscBN import WinDiscBN
import lib_sallybn
from lib_sallybn.GraphDrawer import GraphDrawer
import lib_sallybn.gutil
import lib_sallybn.gwidgets






# Mode for
class Mode(Enum):
    edit = 0
    run = 1


# Mode for edition
class ModeEdit(Enum):
    manual = 0
    vertex = 1
    edge = 2
    delete = 3


FILE_EXTENSION = ".sly"


class WinHandler:
    def __init__(self, window, area, edit_buttons):

        #FIXME statex from other place
        self.window = window
        # self.states = ["true", "false"]

        self.drawer = GraphDrawer(area)
        self.area = area
        self.edit_buttons = edit_buttons

        # Scale
        self.scale = 1
        self.delta_zoom = 0.1
        self.mode_edit = ModeEdit.vertex
        self.mode = Mode.edit

        # Temporal vertex for edge
        self.vertex_1 = None
        self.selected_vetex = None
        self.vertex_count = 1

        # Temporal arrow for mouse motion
        self.tmp_arrow = None


        # Graph
        self.disc_bn = DiscreteBayesianNetworkExt()
        # Window manager for discrete bayesian networks
        self.win_discbn = WinDiscBN(self.disc_bn)

        self.vertex_locations = {}
        # self.edges = []
        # self.states = {}
        # self.cpts = {}

        self.builder = None

        #FIXME change all events for only motion
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.SCROLL_MASK |
                             Gdk.EventMask.SMOOTH_SCROLL_MASK | Gdk.EventMask.ALL_EVENTS_MASK)
        self.area.connect('draw', self.on_drawing_area_draw)

        self.area.connect("motion_notify_event", self.motion_event)
        self.area.connect('button-press-event', self.on_button_press)
        self.area.connect('scroll-event', self.on_scroll)
        self.area.connect('button-release-event', self.on_button_release)

        self.clicks = []
        self.transform = None
        self.trans_point = None

        self.clicked_point = None
        self.dragged = None

    def on_scroll(self, widget, event):
        #print event.direction, event.delta_x, event.delta_y
        self.trans_point = [event.x, event.y]
        self.scale -= self.delta_zoom * event.delta_y

        self.area.queue_draw()
        return True

    def on_save(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
                                       Gtk.FileChooserAction.SAVE,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_SAVE, Gtk.ResponseType.OK))

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Sally files")
        filter_py.add_pattern("*" + FILE_EXTENSION)
        dialog.add_filter(filter_py)

        # response = dialog.run()
        #
        # if response == Gtk.ResponseType.OK:
        #     bn = {
        #         "V": self.vertex_locations,
        #         "E": self.edges,
        #         "S": self.states,
        #         "CPT": self.cpts
        #     }
        #     file_name = dialog.get_filename()
        #     if not file_name.endswith(FILE_EXTENSION):
        #         file_name += FILE_EXTENSION
        #     with open(file_name, 'w') as outfile:
        #         json.dump(bn, outfile)
        #
        # dialog.destroy()


    def on_open(self, widget):
        dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
                                       Gtk.FileChooserAction.OPEN,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        # Filter
        filter_py = Gtk.FileFilter()
        filter_py.set_name("Sally files")
        filter_py.add_pattern("*" + FILE_EXTENSION)
        dialog.add_filter(filter_py)

        #RUN
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            print("File selected: " + dialog.get_filename())
            ## TODO leer json

        dialog.destroy()

    def on_new(self, widget):
        print "new"

    def on_button_release(self, widget, event):
        # Right click
        if event.button == 3:
            return

        p = [event.x, event.y]
        p = self.transform.transform_point(p[0], p[1])

        dx, dy = [self.clicked_point[0] - p[0], self.clicked_point[1] - p[1]]
        click_distance = math.hypot(dx, dy)
        # normal click
        if click_distance < 10.0:
            self.dragged = None
            self.edition_action(p)

        self.clicked_point = None


    def on_button_press(self, widget, event):
        # double
        p = [event.x, event.y]
        p = self.transform.transform_point(p[0], p[1])

        self.selected_vetex = lib_sallybn.gutil.vertex_in_circle(p, self.vertex_locations)

        self.dragged = None

        ## Right click for edit node
        if event.button == 3 and self.selected_vetex is not None:
            self.show_edit_popup(event)
            return True

        ## doble click, open the dialog
        elif event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:

            self.win_discbn.show_cpt_dialog(self.window, self.selected_vetex)
            self.clicked_point = None
            self.selected_vetex = None
            return

        ## Click on edit area
        elif event.button == 1 and self.mode == Mode.edit:
            self.clicked_point = p


    def motion_event(self, widget, event):
        p = [event.x, event.y]
        p = self.transform.transform_point(p[0], p[1])

        ## Dynamic headarrow
        if self.mode == Mode.edit and \
                        self.mode_edit == ModeEdit.edge and \
                        self.selected_vetex is not None:
            self.tmp_arrow = p
            self.area.queue_draw()

        # translate node
        elif self.clicked_point is not None and self.mode == Mode.edit and self.selected_vetex is not None:
            self.vertex_locations[self.selected_vetex] = p
            self.area.queue_draw()

        # translate world
        elif self.clicked_point is not None:
            p = [event.x, event.y]
            p = self.transform.transform_point(p[0], p[1])

            dx, dy = [self.clicked_point[0] - p[0], self.clicked_point[1] - p[1]]
            self.dragged = [-dx, -dy]
            self.area.queue_draw()

    def on_drawing_area_draw(self, drawing_area, cairo):
        cairo.scale(self.scale, self.scale)

        # TODO translate for zoom
        # if self.trans_point is not None:
        #     tx, ty = self.transform.transform_point(self.trans_point[0], self.trans_point[1])
        #     cairo.translate(tx, ty)
        if self.dragged is not None:
            cairo.translate(self.dragged[0], self.dragged[1])
            self.dragged = None

        # print cairo.get_matrix()
        self.transform = cairo.get_matrix()
        self.transform.invert()

        # print self.transform

        self.drawer.draw_background(cairo)

        if self.mode == Mode.edit:
            # Draw selected nodes
            # print "selected vertex:", self.selected_vetex
            if self.selected_vetex is not None:
                self.drawer.draw_selected_vertices(cairo, self.selected_vetex, self.vertex_locations)

                # Draw temporal arrow
                if self.mode_edit == ModeEdit.edge and self.tmp_arrow is not None:
                    tmp_v = {"I": self.vertex_locations[self.selected_vetex], "F": self.tmp_arrow}
                    tmp_e = [["I", "F"]]
                    self.drawer.draw_directed_arrows(cairo, tmp_e, tmp_v, headarrow_d=0)

            # Draw edges
            self.drawer.draw_directed_arrows(cairo, self.disc_bn.get_edges(), self.vertex_locations)
            # Draw nodes
            self.drawer.draw_vertices(cairo, self.vertex_locations)

        elif self.mode == Mode.run:
            # Draw edges
            self.drawer.draw_arrow_box(cairo, self.vertex_locations, self.disc_bn.E)
            # Draw nodes
            self.drawer.draw_boxes(cairo, self.vertex_locations, self.disc_bn)

        return False

    def on_mode(self, radio_tool):
        if not radio_tool.get_active():
            return True

        if radio_tool.get_label() == "bedit":
            self.mode = Mode.edit
            self.set_edit_buttons_visible(True)
        if radio_tool.get_label() == "brun":
            self.mode = Mode.run
            self.set_edit_buttons_visible(False)

        self.area.queue_draw()

    def on_edit_mode(self, radiotool):
        if not radiotool.get_active():
            return True
        # Radio selected
        if radiotool.get_label() == "bvertex":
            self.mode_edit = ModeEdit.vertex
            print "node mode", radiotool.get_active(), self.mode_edit, radiotool.get_label()
        elif radiotool.get_label() == "bedge":
            self.mode_edit = ModeEdit.edge
        elif radiotool.get_label() == "bmanual":
            self.mode_edit = ModeEdit.manual
        elif radiotool.get_label() == "bdelete":
            self.mode_edit = ModeEdit.delete
        else:
            print "not supported"
        self.selected_vetex = None

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)


    def edition_action(self, p):
        # if self.transform is not None:
        # p = self.transform.transform_point(p[0], p[1])

        #### Mode Edit #####
        if self.mode == Mode.edit:

            # search if a node exist in that point
            self.selected_vetex = lib_sallybn.gutil.vertex_in_circle(p, self.vertex_locations)

            ## Mode
            if self.mode_edit == ModeEdit.vertex:
                # Create new Vertex
                if self.selected_vetex is None:
                    vname = 'Variable ' + str(self.vertex_count)
                    # new vertex
                    self.vertex_locations[vname] = p

                    self.disc_bn.add_vertex(vname)

                    self.vertex_count += 1

            elif self.mode_edit == ModeEdit.edge:

                # If there is not a initial vertex selected
                if self.vertex_1 is None and self.selected_vetex is not None:
                    self.vertex_1 = self.selected_vetex
                elif self.vertex_1 is not None and self.selected_vetex is None:
                    #Select anything
                    print "anything selected"
                    self.vertex_1 = None
                elif self.vertex_1 is not None and self.selected_vetex is not None:
                    if not self.vertex_1 == self.selected_vetex and self.selected_vetex is not None:
                        self.disc_bn.add_edge([self.vertex_1, self.selected_vetex])

                        self.vertex_1 = None
                        self.selected_vetex = None
                self.tmp_arrow = None
            elif self.mode_edit == ModeEdit.delete:
                # Delete vertex
                self.vertex_locations.pop(self.selected_vetex)
                # delete edges
                for [v1, v2] in self.disc_bn.E:
                    if v1 == self.selected_vetex or v2 == self.selected_vetex:
                        self.disc_bn.remove_edge([v1, v2])

        ##### Mode run
        elif self.mode == Mode.run:
            pass

        self.area.queue_draw()

    def set_edit_buttons_visible(self, visible):
        for eb in self.edit_buttons:
            eb.set_visible(visible)

    def change_vertex_name_h(self, old_name, new_name):
        #vertex locations
        self.vertex_locations[new_name] = self.vertex_locations.pop(old_name)
        # Change in BN
        self.disc_bn.change_vertex_name(old_name, new_name)

        #selected vertex
        if self.selected_vetex == old_name:
            self.selected_vetex = new_name


    def show_edit_popup(self, event):
        #Draw selected node
        self.area.queue_draw()

        menu = Gtk.Menu()
        menu_it = Gtk.MenuItem()
        menu_it.set_label("Edit")

        menu = Gtk.Menu()
        menuitem = Gtk.MenuItem(label="RadioMenuItem")
        menuitem.set_submenu(menu)
        menu_it = Gtk.MenuItem("Edit Variable")

        # Click on edit vertex data.
        def event_edit(widget, event):
            menu.destroy()
            self.win_discbn.show_cpt_dialog(self.window, self.selected_vetex)

            new_var_name =self.win_discbn.get_var_name()

            if not new_var_name == self.selected_vetex:
                self.change_vertex_name_h(self.selected_vetex, new_var_name)


        menu_it.connect("button-release-event", event_edit)
        menu.append(menu_it)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)