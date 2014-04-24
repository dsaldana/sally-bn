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
import math

from lib_sallybn.disc_bayes_net.CptDialog import CptDialog
from lib_sallybn.disc_bayes_net.DiscreteBayesianNetworkExt import DiscreteBayesianNetworkExt
from lib_sallybn.util import ugraphic
from lib_sallybn.util.ufile import dic_from_json_file, dic_to_file
from libpgm.graphskeleton import GraphSkeleton
from libpgm.nodedata import NodeData
from lib_sallybn.GraphDrawer import GraphDrawer
import lib_sallybn.util.ugraphic
import lib_sallybn
import lib_sallybn.disc_bayes_net.gwidgets
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
    edit = 0
    run = 1


# Mode for edition
class ModeEdit:
    manual = 0
    vertex = 1
    edge = 2


class BoxDiscreteBN(Gtk.Box):
    def __init__(self, window):
        self.window = window

        # Create graphic widgets
        self.box_disc_bn, self.area, self.toolbar_edit, self.bedit, self.brun, self.bclear_evidence = \
            ugraphic.create_widget(
                res.TAB_DISC_BAYES_NET_GLADE,
                ["box_disc_bn", "drawingarea_bn", "toolbar_edit_bn", "bedit", "brun", "bclear_evidence"], self)

        super(BoxDiscreteBN, self).__init__(spacing=1)
        self.pack_start(self.box_disc_bn, True, True, 0)
        self.set_visible(True)

        self.drawer = GraphDrawer(self.area)

        self.mode_edit = ModeEdit.vertex
        self.mode = Mode.edit

        # Temporal vertex for edge
        self.vertex_1 = None
        self.selected_vetex = None
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


    def on_clear_evidence(self, button):
        """
        Event to clear all evidence
        """
        self.evidences = {}
        self.marginals = self.disc_bn.compute_marginals(self.evidences)
        self.area.queue_draw()

    def on_zoom(self, button):
        """
        Zoom event by button.
        """
        self.drawer.restore_zoom()

    def on_button_release(self, widget, event):
        """
        Button release on the drawing area.
        """
        self.button_pressed = False

        # Right click or middle click does not matter
        if event.button > 1:
            return

        p = [event.x, event.y]

        dx, dy = [self.clicked_point[0] - p[0], self.clicked_point[1] - p[1]]
        click_distance = math.hypot(dx, dy)
        # normal click
        if click_distance < 10.0:
            self.editing_action(p)

        self.clicked_point = None

    def on_button_press(self, widget, event):
        """
        Button pressed on drawing area.
        """
        self.button_pressed = True
        p = [event.x, event.y]
        #transformed point
        #trf_p = self.transform.transform_point(p[0],p[1])
        trf_p = self.drawer.transform_point(p)

        if self.mode == Mode.edit:
            # If there is a vertex in the clicked point
            self.selected_vetex = ugraphic.point_in_circle(trf_p, self.vertex_locations)
            # If there is a edge in the clicked point
            if self.selected_vetex is None:
                self.selected_edge = ugraphic.point_in_line(trf_p, self.vertex_locations,
                                                            self.disc_bn.get_edges())

            ## Right click for edit and delete
            if event.button == 3 and (self.selected_vetex
                                      is not None or self.selected_edge is not None):
                self.show_edit_popup(event)
                self.clicked_point = None

            ## double click, open the dialog
            elif event.button == 1 and event.type == Gdk.EventType._2BUTTON_PRESS:
                # Show cpt dialog
                self.show_edit_var_dialog()

                self.clicked_point = None
                self.selected_vetex = None
                return

        elif self.mode == Mode.run:
            # get selected state for evidence
            new_evidence = self.drawer.point_in_state(trf_p, self.vertex_locations, self.marginals)

            if new_evidence is not None:
                v_evid, s_evid = new_evidence
                self.evidences[v_evid] = s_evid
                # compute marginals again
                self.marginals = self.disc_bn.compute_marginals(self.evidences)

        # Normal click
        if event.button == 1:
            self.clicked_point = p


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
            self.set_mode(Mode.edit)

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
        if self.mode == Mode.edit:
            self.toolbar_edit.set_visible(True)
            self.bclear_evidence.set_visible_horizontal(False)
        elif self.mode == Mode.run:
            self.toolbar_edit.set_visible(False)
            self.bclear_evidence.set_visible_horizontal(True)
        self.area.queue_draw()

    def on_organize(self, widget):
        """
        Estimate good places to draw each vertex of the graph.
        """
        self.vertex_locations = ugraphic.create_vertex_locations(self.disc_bn)
        self.area.queue_draw()

    def on_delete(self, *widget):
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
        elif radiotool.get_label() == "bedge":
            self.mode_edit = ModeEdit.edge
        elif radiotool.get_label() == "bmanual":
            self.mode_edit = ModeEdit.manual
        else:
            print "not supported"
        self.selected_vetex = None

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

    def draw_mode_edit(self):
        # Configure drawer
        self.drawer.set_boxes({})
        self.drawer.set_edges_type_box([])

        if self.selected_edge is not None:
            self.drawer.set_selected_edges([self.selected_edge])
        if self.selected_vetex is not None:
            self.drawer.set_selected_vertices([self.selected_vetex])

        self.drawer.set_vertices(self.vertex_locations)
        self.drawer.set_edges_type_vertex(self.disc_bn.get_edges())

        self.drawer.repaint()

    def draw_mode_run(self):
        # Configure drawer
        self.drawer.set_selected_edges([])
        self.drawer.set_selected_vertices([])
        self.drawer.set_vertices({})
        self.drawer.set_edges_type_vertex([])

        # todo boxes contains more information
        self.drawer.set_boxes(self.vertex_locations)
        self.drawer.set_edges_type_box(self.disc_bn.get_edges())


    def editing_action(self, p):
        """
        Action for adding vertices or edges.
        """
        # if self.transform is not None:
        p = self.drawer.transform_point(p)
        # p = [p[0] - self.translation[0], p[1] - self.translation[1]]

        #### Mode Edit #####
        if self.mode == Mode.edit:


            # search if a node exist in that point
            self.selected_vetex = lib_sallybn.util.ugraphic.point_in_circle(p, self.vertex_locations)

            self.draw_mode_edit()

            ## Mode edit VERTEX
            if self.mode_edit == ModeEdit.vertex:
                # Create new Vertex
                if self.selected_vetex is None and self.selected_edge is None:
                    vname = self.get_new_vertex_name()
                    # new vertex
                    self.vertex_locations[vname] = p
                    self.disc_bn.add_vertex(vname)

            ####### MODE EDIT EDGE
            elif self.mode_edit == ModeEdit.edge:

                # If there is not a initial vertex selected
                if self.vertex_1 is None and self.selected_vetex is not None:
                    self.vertex_1 = self.selected_vetex

                # If there is an initial vertex
                elif self.vertex_1 is not None and self.selected_vetex is None:
                    #Select anything
                    self.vertex_1 = None
                    # draw a dynamic arrow
                    self.drawer.set_dynamic_arrow(self.selected_edge)
                elif self.vertex_1 is not None and self.selected_vetex is not None:
                    if not self.vertex_1 == self.selected_vetex and self.selected_vetex is not None:
                        self.disc_bn.add_edge([self.vertex_1, self.selected_vetex])

                        self.vertex_1 = None
                        self.selected_vetex = None
                self.tmp_arrow = None

        ##### Mode run
        elif self.mode == Mode.run:
            self.draw_mode_run()

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

        # Edit selected vertex
        if self.selected_vetex is not None:
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
        cpt_dialog.show_cpt_dialog(self.window, new_disc_bn, self.selected_vetex)

        new_var_name = cpt_dialog.get_var_name()

        ## Cancel button, new_var_name is assigned
        if new_var_name is None:
            return

        self.disc_bn = new_disc_bn

        if not new_var_name == self.selected_vetex:
            self.change_vertex_name_h(self.selected_vetex, new_var_name)

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
                self.vertex_locations = json_data["vertex_loc"]
            else:
                self.vertex_locations = ugraphic.create_vertex_locations(self.disc_bn)

            self.draw_mode_edit()
        except Exception:
            ugraphic.show_warning(self.window, "Error loading the Bayesian Network")
            return

