from gi.repository import Gtk, Gdk
import math

from enum import Enum

from lib_sallybn.disc_bayes_net.CptDialog import CptDialog
from lib_sallybn.disc_bayes_net.DiscreteBayesianNetworkExt import DiscreteBayesianNetworkExt
from lib_sallybn.util import ugraphic
from lib_sallybn.util.ufile import dic_from_json_file, dic_to_file
from libpgm.graphskeleton import GraphSkeleton
from libpgm.nodedata import NodeData
import lib_sallybn
from lib_sallybn.GraphDrawer import GraphDrawer
import lib_sallybn.util.ugraphic
import lib_sallybn.disc_bayes_net.gwidgets
import lib_sallybn.util.resources as res






## Constants
FILE_EXTENSION = ".sly"
DEFAULT_NODE_NAME = 'Variable'

## Enumerations
# Mode for
class Mode(Enum):
    edit = 0
    run = 1


# Mode for edition
class ModeEdit(Enum):
    manual = 0
    vertex = 1
    edge = 2


class BoxDiscreteBN(Gtk.Box):
    def __init__(self, window):
        self.window = window

        # Create graphic widgets
        # other "bvertex", "bdelete", "bedge"
        self.box_disc_bn, self.area, self.edit_toolbar = \
            ugraphic.create_widget(
                res.TAB_DISC_BAYES_NET_GLADE,
                ["box_disc_bn", "drawingarea_bn", "toolbar_edit_bn"], self)

        super(BoxDiscreteBN, self).__init__(spacing=1)
        self.pack_start(self.box_disc_bn, True, True, 0)
        self.set_visible(True)

        self.drawer = GraphDrawer(self.area)

        # Scale
        self.scale = 1
        self.delta_zoom = 0.1
        self.mode_edit = ModeEdit.vertex
        self.mode = Mode.edit

        # Temporal vertex for edge
        self.vertex_1 = None
        self.selected_vetex = None
        self.selected_edge = None
        self.vertex_count = 1

        # Temporal arrow for mouse motion
        self.tmp_arrow = None

        # Graph
        self.disc_bn = DiscreteBayesianNetworkExt()
        # Window manager for discrete bayesian networks
        self.cpt_dialog = CptDialog()

        self.vertex_locations = {}
        self.builder = None

        #FIXME change all events for only motion
        # self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.SCROLL_MASK |
        #                      Gdk.EventMask.SMOOTH_SCROLL_MASK | Gdk.EventMask.ALL_EVENTS_MASK)
        # self.area.connect('draw', self.on_drawing_area_draw)

        # self.area.connect("motion_notify_event", self.motion_event)
        # self.area.connect('button-press-event', self.on_button_press)
        # self.area.connect('scroll-event', self.on_scroll)
        # self.area.connect('button-release-event', self.on_button_release)


        self.clicks = []
        self.transform = None
        self.trans_point = None

        self.clicked_point = None
        self.dragged = None

    def get_box(self):
        return self.box_disc_bn

    def on_scroll(self, widget, event):
        #print event.direction, event.delta_x, event.delta_y
        self.trans_point = [event.x, event.y]
        self.scale -= self.delta_zoom * event.delta_y

        self.area.queue_draw()
        return True


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
            self.editing_action(p)

        self.clicked_point = None


    def on_button_press(self, widget, event):
        # double
        p = [event.x, event.y]
        p = self.transform.transform_point(p[0], p[1])

        self.selected_vetex = lib_sallybn.util.ugraphic.vertex_in_circle(p, self.vertex_locations)

        if self.selected_vetex is None:
            self.selected_edge = lib_sallybn.util.ugraphic.edge_in_point(p,
                                                                         self.vertex_locations,
                                                                         self.disc_bn.get_edges())

        self.dragged = None

        ## Right click for edit node
        if event.button == 3 and self.selected_vetex is not None:
            self.show_edit_popup(event)
            return True

        ## doble click, open the dialog
        elif event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:

            self.cpt_dialog.show_cpt_dialog(self.window, self.disc_bn, self.selected_vetex)
            self.clicked_point = None
            self.selected_vetex = None
            # return True

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

        #### ON EDITION MODE ###
        if self.mode == Mode.edit:
            # Draw selected nodes
            # print "selected vertex:", self.selected_vetex
            if self.selected_vetex is not None:
                self.drawer.draw_selected_vertex(cairo, self.selected_vetex, self.vertex_locations)

                # Draw temporal arrow
                if self.mode_edit == ModeEdit.edge and self.tmp_arrow is not None:
                    tmp_v = {"I": self.vertex_locations[self.selected_vetex], "F": self.tmp_arrow}
                    tmp_e = [["I", "F"]]
                    self.drawer.draw_directed_arrows(cairo, tmp_e, tmp_v, headarrow_d=0)
            elif self.selected_edge is not None:
                print "selected edge", self.selected_edge
                self.drawer.draw_selected_edge(cairo, self.selected_edge, self.vertex_locations)

            # Draw edges
            self.drawer.draw_directed_arrows(cairo, self.disc_bn.get_edges(), self.vertex_locations)
            # Draw nodes
            self.drawer.draw_vertices(cairo, self.vertex_locations)

        #### ON RUN MODE ###
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
            self.edit_toolbar.set_visible(True)
        if radio_tool.get_label() == "brun":
            self.mode = Mode.run
            self.edit_toolbar.set_visible(False)

        self.area.queue_draw()

    def on_organize(self, widget):
        self.vertex_locations = ugraphic.create_vertex_locations(self.disc_bn)
        self.area.queue_draw()


    def on_key_area(self, widget, event):
        print "key", event

    def on_delete(self, widget):
        # Delete vertex
        if self.selected_vetex is not None:
            self.vertex_locations.pop(self.selected_vetex)

            # Delete from model
            self.disc_bn.remove_vertex(self.selected_vetex)

            # Non selected vertex
            self.selected_vetex = None
        # Delete edge
        elif self.selected_edge is not None:
            # Delete from model
            self.disc_bn.remove_edge(self.selected_edge)
            # Non selected
            self.selected_edge = None
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
        else:
            print "not supported"
        self.selected_vetex = None

    def get_new_vertex_name(self):
        counter = 1
        new_name = DEFAULT_NODE_NAME + ' ' + str(counter)

        while new_name in self.disc_bn.get_vertices():
            counter += 1
            new_name = DEFAULT_NODE_NAME + ' ' + str(counter)
        return new_name

    def editing_action(self, p):
        # if self.transform is not None:
        # p = self.transform.transform_point(p[0], p[1])

        #### Mode Edit #####
        if self.mode == Mode.edit:

            # search if a node exist in that point
            self.selected_vetex = lib_sallybn.util.ugraphic.vertex_in_circle(p, self.vertex_locations)

            ## Mode VERTEX
            if self.mode_edit == ModeEdit.vertex:
                # Create new Vertex
                if self.selected_vetex is None and self.selected_edge is None:
                    vname = self.get_new_vertex_name()
                    # new vertex
                    self.vertex_locations[vname] = p

                    self.disc_bn.add_vertex(vname)

                    self.vertex_count += 1

            ## Mode EDGE
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




        ##### Mode run
        elif self.mode == Mode.run:
            pass

        self.area.queue_draw()


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
            self.cpt_dialog.show_cpt_dialog(self.window, self.disc_bn, self.selected_vetex)

            new_var_name = self.cpt_dialog.get_var_name()

            if not new_var_name == self.selected_vetex:
                self.change_vertex_name_h(self.selected_vetex, new_var_name)


        menu_it.connect("button-release-event", event_edit)
        menu.append(menu_it)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)


    def save_bn_to_file(self, file_name):
        # if does not have extension
        if not file_name.endswith(FILE_EXTENSION):
            file_name += FILE_EXTENSION

        bn = {
            "vertex_loc": self.vertex_locations,
            "E": self.disc_bn.get_edges(),
            "V": self.disc_bn.get_vertices(),
            "Vdata": self.disc_bn.get_vdata()}

        dic_to_file(bn, file_name)


    def load_bn_from_file(self, file_name):
        #### Load BN
        nd = NodeData()
        skel = GraphSkeleton()
        nd.load(file_name)  # any input file
        skel.load(file_name)

        # topologically order graphskeleton
        try:
            skel.toporder()
        except ValueError:
            print ValueError
            return

        # load bayesian network
        self.disc_bn = DiscreteBayesianNetworkExt(skel, nd)

        ### Load Vertex locations
        json_data = dic_from_json_file(file_name)
        # Vertex locations
        if "vertex_loc" in json_data.keys():
            self.vertex_locations = json_data["vertex_loc"]
        else:
            self.vertex_locations = ugraphic.create_vertex_locations(self.disc_bn)
        print self.vertex_locations




