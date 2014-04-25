# ----------------------------------------------------------------------------
#
# Sally BN: An Open-Source Framework for Bayesian Networks.
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
from gi.repository import Gtk, Gdk
from lib_sallybn.disc_bayes_net.CptDialog import CptDialog
from lib_sallybn.disc_bayes_net.DiscreteBayesianNetworkExt import DiscreteBayesianNetworkExt
from lib_sallybn.drawer.GPoint import GPoint
from lib_sallybn.drawer.GStateBox import GStateBox
from lib_sallybn.drawer.GraphDrawer import GraphDrawer
from lib_sallybn.drawer.GArrow import GArrow
from lib_sallybn.drawer.GVertex import GVertex

from lib_sallybn.util import ugraphic
from lib_sallybn.util.ufile import dic_from_json_file, dic_to_file
from libpgm.graphskeleton import GraphSkeleton
from libpgm.nodedata import NodeData
import lib_sallybn.util.resources as res




## Constants
FILE_EXTENSION = ".sly"
DEFAULT_NODE_NAME = 'Variable'

KEY_SUPR_CODE = 65535
KEY_E_CODE = 101
KEY_R_CODE = 114

## Enumerations
# Mode for
class Mode:
    edit_vertex = 0
    edit_edge = 1
    run = 2


class BoxDiscreteBN(Gtk.Box):
    def __init__(self, window):
        self.window = window

        # Create graphic widgets
        self.box_disc_bn, self.drawing_box, self.toolbar_edit, self.bedit, self.brun, self.bclear_evidence = \
            ugraphic.create_widget(
                res.TAB_DISC_BAYES_NET_GLADE,
                ["box_disc_bn", "drawing_box", "toolbar_edit_bn", "bedit", "brun", "bclear_evidence"], self)

        super(BoxDiscreteBN, self).__init__(spacing=1)
        self.pack_start(self.box_disc_bn, True, True, 0)
        self.set_visible(True)

        self.drawer = GraphDrawer()
        self.drawing_box.pack_start(self.drawer.get_drawing_area(), True, True, 0)

        self.mode = Mode.edit_vertex

        # Temporal vertex for edge
        self.vertex_1 = None
        self.selected_vertex = None
        self.selected_edge = None
        self.marginals = None
        self.evidences = {}

        # Temporal arrow for mouse motion
        self.tmp_arrow = None

        # Graph
        self.disc_bn = DiscreteBayesianNetworkExt()

        # Vertex locations to draw
        self.vertex_locations = {}

        self.clicked_point = None
        self.button_pressed = False

        # connect listeners
        self.drawer.clicked_element_listener = self.clicked_element
        self.drawer.clicked_clear_space_listener = self.clicked_clear_space
        self.drawer.right_click_elem_listener = self.right_clicked_elem
        self.drawer.double_clicked_element_listener = self.double_click_on_elem


    def double_click_on_elem(self, elem):
        print "ouble click"
        # Show cpt dialog
        self.show_edit_var_dialog()

        self.clicked_point = None
        self.selected_vertex = None


    def clicked_clear_space(self, p):
        if self.mode == Mode.edit_vertex:
            # Crate vertex
            vname = self.get_new_vertex_name()
            # new vertex
            self.vertex_locations[vname] = GPoint(p[0], p[1])
            self.disc_bn.add_vertex(vname)

        elif self.mode == Mode.edit_edge:
            self.drawer.dynamic_arrow = None
            self.selected_vertex = None

        self.draw_graph()

    def right_clicked_elem(self, elem, event):
        if self.mode == Mode.edit_vertex or self.mode == Mode.edit_edge:
            if isinstance(elem, GVertex) or isinstance(elem, GArrow):
                self.show_edit_popup(event)

    def clicked_element(self, gelement):
        if self.mode == Mode.edit_vertex:
            gelement.selected = True

            # False others
            if isinstance(gelement, GVertex):
                self.selected_vertex = gelement.name

        elif self.mode == Mode.edit_edge:
            if isinstance(gelement, GVertex):
                new_selection = gelement.name

                if self.selected_vertex is None:
                    self.selected_vertex = new_selection
                    self.drawer.dynamic_arrow = self.vertex_locations[new_selection]
                else:
                    self.disc_bn.add_edge([self.selected_vertex, new_selection])
                    self.selected_vertex = None
                    self.drawer.dynamic_arrow = None

            # elif isinstance(gelement, GArrow):
            #     self.selected_edge = G

        elif self.mode == Mode.run:
            # get selected state for evidence
            if isinstance(gelement, GStateBox):
                new_evidence = gelement.selected_state
                if new_evidence is not None:
                    self.evidences[gelement.name] = new_evidence
                    # compute marginals again
                    self.marginals = self.disc_bn.compute_marginals(self.evidences)
                    self.draw_graph()

        self.drawer.repaint()

    def on_clear_evidence(self, button):
        """
        Event to clear all evidence
        """
        self.evidences = {}
        self.marginals = self.disc_bn.compute_marginals(self.evidences)
        self.drawer.repaint()

    def on_zoom(self, button):
        """
        Zoom event by button.
        """
        self.drawer.restore_zoom()

    def on_key_press(self, widget, event):
        """
        Key event generated by box container.
        """
        # Supr key is pressed
        if event.keyval == KEY_SUPR_CODE:
            self.on_delete(None)
        elif event.keyval == KEY_E_CODE:
            self.bedit.set_active(True)
        elif event.keyval == KEY_R_CODE:
            self.brun.set_active(True)

    def on_show(self, widget, event):
        print "show"


    def on_mode(self, radio_tool):
        """
        Event to choose the 'edit mode' or the 'run mode'.
        """
        if not radio_tool.get_active():
            return True

        if radio_tool.get_label() == "bedit":
            self.set_mode(Mode.edit_vertex)

        if radio_tool.get_label() == "brun":
            # Validate BN
            for v in self.disc_bn.get_vertices():
                # Validate cycles
                try:
                    self.disc_bn.toporder()
                except Exception:
                    ugraphic.show_warning(self.window,
                                          "The Bayesian Network contains cycles.")
                    return

                # Validate that the BN has all the cpts
                ok = self.disc_bn.validate_cprob(v)
                if not ok:
                    ugraphic.show_warning(self.window,
                                          v + " is not valid.",
                                          "please, check the probability table.")
                    self.bedit.set_active(True)
                    return
            # compute marginals
            self.marginals = self.disc_bn.compute_marginals(self.evidences)
            self.set_mode(Mode.run)


    def set_mode(self, mode):
        """
        Select Edit or Run mode.
        """
        self.mode = mode
        if self.mode == Mode.edit_edge or self.mode == Mode.edit_vertex:
            self.toolbar_edit.set_visible(True)
            self.bclear_evidence.set_visible_horizontal(False)

        elif self.mode == Mode.run:
            self.toolbar_edit.set_visible(False)
            self.bclear_evidence.set_visible_horizontal(True)

        self.selected_vertex = None
        self.selected_edge = None
        self.draw_graph()


    def on_organize(self, widget):
        """
        Estimate good places to draw each vertex of the graph.
        """
        v_locts = ugraphic.create_vertex_locations(self.disc_bn)
        self.dict_to_gpoints(v_locts)
        self.draw_graph()

    def dict_to_gpoints(self, v_locts):
        for vname, point in v_locts.items():
            self.vertex_locations[vname] = GPoint(point[0], point[1])

    def gpoints_to_dict(self):
        l_loc = {}
        for vname, gpoint in self.vertex_locations.items():
            l_loc[vname] = gpoint

        return l_loc

    def on_delete(self, *widget):
        # Delete vertex
        if self.selected_vertex is not None:
            self.vertex_locations.pop(self.selected_vertex)

            # Delete from model
            self.disc_bn.remove_vertex(self.selected_vertex)

            # Non selected vertex
            self.selected_vertex = None
            #Draw
            self.drawer.set_selected_vertices([])

        # Delete edge
        elif self.selected_edge is not None:
            # Delete from model
            self.disc_bn.remove_edge(self.selected_edge)
            # Non selected
            self.selected_edge = None
            self.drawer.set_selected_edges([])

        # Draw
        self.drawer.repaint()

    def get_new_vertex_name(self):
        """ Vertex name generator to create incremental variables and does not generate
        incompatibility with assigned names by user .
        """
        counter = 1
        new_name = DEFAULT_NODE_NAME + ' ' + str(counter)

        while new_name in self.disc_bn.get_vertices():
            counter += 1
            new_name = DEFAULT_NODE_NAME + ' ' + str(counter)
        return new_name

    def draw_graph(self):
        if self.mode == Mode.edit_vertex or self.mode == Mode.edit_edge:
            self.draw_mode_edit()
        else:
            self.draw_mode_run()

    def draw_mode_edit(self):
        ## Configure drawer
        vl = self.vertex_locations

        # Graphic elements
        gelements = []
        # Edges
        for e in self.disc_bn.get_edges():
            arrow = GArrow(self.vertex_locations[e[0]], self.vertex_locations[e[1]])
            if e == self.selected_edge:
                arrow.selected = True
            gelements.append(arrow)
        # Vertices
        for vname, p in vl.items():
            v = GVertex(p, vname)
            v.translatable = True
            if self.selected_vertex == vname:
                v.selected = True
            gelements.append(v)

        self.drawer.set_graphic_objects(gelements)
        self.drawer.repaint()

    def draw_mode_run(self):
        ## Configure drawer
        vl = self.vertex_locations

        # Graphic elements
        gelements = []
        # Edges
        for e in self.disc_bn.get_edges():
            arrow = GArrow(self.vertex_locations[e[0]], self.vertex_locations[e[1]])
            gelements.append(arrow)

        for vname, p in vl.items():

            evidence = {}
            if vname in self.evidences:
                evidence = self.evidences[vname]
            b = GStateBox(p, vname, self.marginals[vname], evidence)
            b.translatable = True
            gelements.append(b)

        self.drawer.set_graphic_objects(gelements)
        self.drawer.repaint()

    def on_edit_mode(self, radiotool):
        if not radiotool.get_active():
            return True
        # Radio selected
        if radiotool.get_label() == "bvertex":
            self.mode = Mode.edit_vertex
        elif radiotool.get_label() == "bedge":
            self.mode = Mode.edit_edge
        elif radiotool.get_label() == "bmanual":
            pass
        else:
            print "not supported"

        # No selections
        self.selected_edge = None
        self.selected_vertex = None
        self.drawer.repaint()

    def editing_action(self, p):
        """
        Action for adding vertices or edges.
        """
        # if self.transform is not None:
        p = self.drawer.transform_point(p)
        # p = [p[0] - self.translation[0], p[1] - self.translation[1]]

        #### Mode Edit #####
        self.draw_mode_edit()

        ## Mode edit VERTEX


        ####### MODE EDIT EDGE
        if self.mode_edit == Mode.edge:

            # If there is not a initial vertex selected
            if self.vertex_1 is None and self.selected_vertex is not None:
                self.vertex_1 = self.selected_vertex

            # If there is an initial vertex
            elif self.vertex_1 is not None and self.selected_vertex is None:
                #Select anything
                self.vertex_1 = None
                # draw a dynamic arrow
                self.drawer.set_dynamic_arrow(self.selected_edge)
            elif self.vertex_1 is not None and self.selected_vertex is not None:
                if not self.vertex_1 == self.selected_vertex and self.selected_vertex is not None:
                    self.disc_bn.add_edge([self.vertex_1, self.selected_vertex])

                    self.vertex_1 = None
                    self.selected_vertex = None
            self.tmp_arrow = None

        ##### Mode run
        # elif self.mode == Mode.run:
        #     self.draw_mode_run()

        self.drawer.repaint()

    def change_vertex_name_h(self, old_name, new_name):
        #vertex locations
        self.vertex_locations[new_name] = self.vertex_locations.pop(old_name)
        # Change in BN
        self.disc_bn.change_vertex_name(old_name, new_name)

        #selected vertex
        if self.selected_vertex == old_name:
            self.selected_vertex = new_name

    def show_edit_popup(self, event):
        #Draw selected node
        self.drawer.repaint()

        menu = Gtk.Menu()
        menu_it = Gtk.MenuItem()
        menu_it.set_label("Edit")

        menu = Gtk.Menu()
        menuitem = Gtk.MenuItem(label="RadioMenuItem")
        menuitem.set_submenu(menu)

        # Edit selected vertex
        if self.selected_vertex is not None:
            menu_it = Gtk.MenuItem("Edit Variable")

            # Click on edit vertex data.
            def event_edit(widget, event):
                menu.destroy()
                self.show_edit_var_dialog()

            menu_it.connect("button-release-event", event_edit)
            menu.append(menu_it)

        # Delete variable or edge
        menu_it_del = Gtk.MenuItem("Delete")
        menu_it_del.connect("button-release-event", self.on_delete)
        menu.append(menu_it_del)

        menu.show_all()
        menu.popup(None, None, None, None, event.button, event.time)

    def show_edit_var_dialog(self):
        cpt_dialog = CptDialog()
        # Create clone of disc_bn
        new_disc_bn = self.disc_bn.clone()
        cpt_dialog.show_cpt_dialog(self.window, new_disc_bn, self.selected_vertex)

        new_var_name = cpt_dialog.get_var_name()

        ## Cancel button, new_var_name is assigned
        if new_var_name is None:
            return

        self.disc_bn = new_disc_bn

        if not new_var_name == self.selected_vertex:
            self.change_vertex_name_h(self.selected_vertex, new_var_name)


    def save_bn_to_file(self, file_name):
        # if does not have extension
        if not file_name.endswith(FILE_EXTENSION):
            file_name += FILE_EXTENSION

        bn = {
            "vertex_loc": self.gpoints_to_dict(),
            "E": self.disc_bn.get_edges(),
            "V": self.disc_bn.get_vertices(),
            "Vdata": self.disc_bn.get_vdata()}

        dic_to_file(bn, file_name)

    def load_bn_from_file(self, file_name):
        try:
            #### Load BN
            nd = NodeData()
            skel = GraphSkeleton()
            nd.load(file_name)  # any input file
            skel.load(file_name)

            # topologically order graphskeleton
            skel.toporder()

            # load bayesian network
            self.disc_bn = DiscreteBayesianNetworkExt(skel, nd)

            ### Load Vertex locations
            json_data = dic_from_json_file(file_name)
            # Vertex locations
            if "vertex_loc" in json_data.keys():
                self.dict_to_gpoints(json_data["vertex_loc"])
            else:
                vl = ugraphic.create_vertex_locations(self.disc_bn)
                self.dict_to_gpoints(vl)

        except Exception:
            ugraphic.show_warning(self.window, "Error loading the Bayesian Network", Exception)
            return

        self.draw_mode_edit()
