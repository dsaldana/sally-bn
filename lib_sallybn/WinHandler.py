from gi.repository import Gtk, Gdk
import math

from enum import Enum

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


default_states = ["true", "false"]


class WinHandler:
    def __init__(self, area, edit_buttons):

        #FIXME statex from other place
        self.states = ["true", "false"]

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
        self.vertices = {}
        self.edges = []
        self.states = {}

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

        self.selected_vetex = lib_sallybn.gutil.vertex_in_circle(p, self.vertices)

        self.dragged = None

        ## Right click for edit node
        if event.button == 3 and self.selected_vetex is not None:
            #Draw selected node
            self.area.queue_draw()
            print "right click"
            menu = Gtk.Menu()
            menu_it = Gtk.MenuItem()
            menu_it.set_label("Edit")

            menu = Gtk.Menu()
            menuitem = Gtk.MenuItem(label="RadioMenuItem")
            menuitem.set_submenu(menu)
            menu_it = Gtk.MenuItem("Edit Variable")

            def event_edit(widget, event):
                menu.set_visible(False)
                self.show_cpt_dialog(self.selected_vetex)


            menu_it.connect("button-release-event", event_edit)
            menu.append(menu_it)

            menu.show_all()
            menu.popup(None, None, None, None, event.button, event.time)

            return True

        ## doble click, open the dialog
        elif event.type == Gdk.EventType._2BUTTON_PRESS:
            self.clicked_point = None
            print "doble click"
            self.selected_vetex = None
            self.show_cpt_dialog(self.selected_vetex)
            return

        ## Click
        elif self.mode == Mode.edit:
            self.clicked_point = p

    def create_widget(self, *names):
        # GTK builder
        builder = Gtk.Builder()
        builder.add_from_file(lib_sallybn.SallyApp.glade_file)

        return [builder.get_object(wname) for wname in names]


    def show_cpt_dialog(self, selected_vetex):

        cpt_dialog, treeview_cpt, text_var_name = \
            self.create_widget("dialog_cpt",
                               "treeview_cpt", "text_var_name")
        cpt_dialog.set_modal(True)
        text_var_name.set_text(selected_vetex)
        # load info for CPT
        gtable = lib_sallybn.gwidgets.GraphicCptTable(self.vertices,
                                                      self.edges,
                                                      self.states,
                                                      self.selected_vetex,
                                                      view=treeview_cpt)

        cpt_dialog.run()

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
            self.vertices[self.selected_vetex] = p
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

        print cairo.get_matrix()
        self.transform = cairo.get_matrix()
        self.transform.invert()

        # print self.transform

        self.drawer.draw_background(cairo)

        if self.mode == Mode.edit:
            # Draw selected nodes
            if self.selected_vetex is not None:
                self.drawer.draw_selected_vertices(cairo, self.selected_vetex, self.vertices)

                # Draw temporal arrow
                if self.mode_edit == ModeEdit.edge and self.tmp_arrow is not None:
                    tmp_v = {"I": self.vertices[self.selected_vetex], "F": self.tmp_arrow}
                    tmp_e = [["I", "F"]]
                    self.drawer.draw_directed_arrows(cairo, tmp_e, tmp_v, headarrow_d=0)

            # Draw edges
            self.drawer.draw_directed_arrows(cairo, self.edges, self.vertices)
            # Draw nodes
            self.drawer.draw_vertices(cairo, self.vertices)

        elif self.mode == Mode.run:
            # Draw edges
            self.drawer.draw_arrow_box(cairo, self.vertices, self.edges)
            # Draw nodes
            self.drawer.draw_boxes(cairo, self.vertices, self.states)

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

    def onButtonPressed(self, button):
        print("Hello World!")

    def edition_action(self, p):
        # if self.transform is not None:
        # p = self.transform.transform_point(p[0], p[1])

        #### Mode Edit #####
        if self.mode == Mode.edit:

            # search if a node exist in that point
            self.selected_vetex = lib_sallybn.gutil.vertex_in_circle(p, self.vertices)

            ## Mode
            if self.mode_edit == ModeEdit.vertex:
                # Create new Vertex
                if self.selected_vetex is None:
                    vname = 'Variable ' + str(self.vertex_count)
                    # new vertex
                    self.vertices[vname] = p
                    self.states[vname] = list(default_states)
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
                        self.edges.append([self.vertex_1, self.selected_vetex])
                        self.vertex_1 = None
                        self.selected_vetex = None
                self.tmp_arrow = None
            elif self.mode_edit == ModeEdit.delete:
                # Delete vertex
                self.vertices.pop(self.selected_vetex)
                # delete edges
                for [v1, v2] in self.edges:
                    if v1 == self.selected_vetex or v2 == self.selected_vetex:
                        self.edges.remove([v1, v2])

        ##### Mode run
        elif self.mode == Mode.run:
            pass

        self.area.queue_draw()

    def set_edit_buttons_visible(self, visible):
        for eb in self.edit_buttons:
            eb.set_visible(visible)

