### Graphic widgets

# Sally-BN
# Mavrin
# Johny Five
# Rose
# Bender
# Dorian

from gi.repository import Gtk
from gi.repository import Pango
import random

import util


NEW_STATE_NAME = "-Click here for new state-"


class StatesTable:
    def __init__(self, states, state_changed_func, view, badd_state, bremove_state):
        self.states = states
        self.view = view
        self.state_changed_func = state_changed_func
        self.model = None
        self._modify_treeview_for_states()

        badd_state.connect("clicked", self._add_state)
        bremove_state.connect("clicked", self._remove_state)

    def _add_state(self, widget):
        self.model.append(["New state"])

    def _remove_state(self, widget):
        if len(self.model) != 0:
            (model, selected_rows) = self.view.get_selection().get_selected()
            if selected_rows is not None:
                print "%s has been removed" %(self.model[selected_rows][0])
                self.model.remove(selected_rows)

    def _modify_treeview_for_states(self):
        ### MODEL
        self.model = Gtk.ListStore(str)
        self.view.set_model(self.model)

        # fill states
        for state in self.states:
            self.model.append([state])
        # New state
        # self.model.append([NEW_STATE_NAME, Gtk.STOCK_ADD])

        ### VIEW
        cell = Gtk.CellRendererText()
        cell.props.editable = True
        # Call signal
        cell.connect("edited", self.text_edited)

        # the column is created
        col = Gtk.TreeViewColumn("States", cell, text=0)

        # append to the tree view
        self.view.append_column(col)

        ## Icon
        # renderer_pixbuf = Gtk.CellRendererPixbuf()
        # column_pixbuf = Gtk.TreeViewColumn("", renderer_pixbuf, stock_id=1)
        # self.view.append_column(column_pixbuf)
        # Call signal
        # renderer_pixbuf.connect("clicked", self.text_edited)

    def text_edited(self, widget, path, text):
        #1 remove the % symbol and spaces
        # text = text.replace("%","")
        # text = text.replace(" ","")
        print text
        # #2 validate the number between 0 and 100
        # val = float(text)
        # if val < 0 or val > 100:
        #     return
        # #3 add the text
        # # text = str(val) + "%"
        # col_number = self.editable_cells[widget]
        self.model[path][0] = text


class GraphicCptTable:
    def __init__(self, vertices, edges, states, cpts, query_v, view=Gtk.TreeView()):
        """
        Create a tree view for the CPT of the node query_v
        :param vertices:
        :param edges:
        :param states:
        :param query_v:
        :return:
        """
        self.cpts = cpts
        self.cpt = None
        self.query_v = query_v
        self.states = states
        self.vertices = vertices
        self.edges = edges

        self.parents = None
        ### DATA MODEL
        self.model = None
        self.editable_cells = {}
        self.parents

        self.widget = self._modify_treeview_for_cpt(view)


    def _modify_treeview_for_cpt(self, view):
        """
        Create a tree view for the CPT of the node query_v

        :return: a treeview widget
        """
        ### Detect parents
        self.parents = util.get_parents(self.query_v, self.edges)

        # number of columns
        n_state_cols = len(self.states[self.query_v])
        # Columns for titles
        n_parent_cols = len(self.parents)

        # TODO Validate parents not zero states

        # number of rows
        n_rows = 1
        for p in self.parents:
            n_rows *= len(self.states[p])

        # data types for parents
        parent_types = [str for i in self.parents]
        # the data in the model (three strings for each row, one for each column)
        cpt_types = [str for i in self.states[self.query_v]]
        # all parent + cpt types
        all_types = parent_types + cpt_types

        print all_types

        ### DATA MODEL
        self.model = Gtk.ListStore(*all_types)
        view.set_model(self.model)


        # FILL CLEAN CPT
        parents_matrix = util.parent_states(self.parents, self.states)

        # Use the loaded CPT
        if self.query_v in self.cpts:
            print "rows", self.cpts and len(self.cpts[self.query_v]) == n_rows
            print "cols", len(self.cpts[self.query_v][0])
            print "cos2", n_state_cols
        # if the table already exists, if nxm is right
        if self.query_v in self.cpts and len(self.cpts[self.query_v]) == n_rows and \
                        len(self.cpts[self.query_v][0]) == n_state_cols:
            self.cpt = self.cpts[self.query_v]
        ## Create a new CPT
        else:
            print "new cpt"
            self.cpt = [["0.0"] * n_state_cols for i in range(n_rows)]

        # PUT CPT
        for l in range(n_rows):
            line = self.cpt[l]
            line = [str(v) for v in line]
            # Fill for no parents
            if len(self.parents) == 0:
                self.model.append(line)
            # With parents
            else:
                self.model.append(parents_matrix[l] + line)
        ### end fill data

        # Table titles
        table_titles = self.parents + [s + "(%)" for s in self.states[self.query_v]]

        # Format for each column
        for i in range(len(table_titles)):
            # cellrenderer to render the text
            cell = Gtk.CellRendererText()

            # Title in bold
            if i < n_parent_cols:
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD
                cell.props.background = "gray"

            else:
                cell.props.xalign = 1.0
                cell.props.editable = True
                self.editable_cells[cell] = i

                # Call signal
                cell.connect("edited", self.text_edited)

            # the column is created
            col = Gtk.TreeViewColumn(table_titles[i], cell, text=i)

            # append to the tree view
            view.append_column(col)

        return view

    ## Event for Edited cells
    def text_edited(self, widget, path, text):
        #1 remove the % symbol and spaces
        # text = text.replace("%","")
        # text = text.replace(" ","")
        print text
        #2 validate the number between 0 and 100
        val = float(text)
        if val < 0 or val > 100:
            return
        #3 add the text
        # text = str(val) + "%"
        col_number = self.editable_cells[widget]
        self.model[path][col_number] = text

    def fill_random(self):
        # number of  columns
        n_state_cols = len(self.states[self.query_v])

        # FILL DATA
        parents_matrix = util.parent_states(self.parents, self.states)

        for i in range(len(parents_matrix)):
            state_values = [random.random() for j in range(n_state_cols)]
            total_sum = sum(state_values)
            state_values = [str(100 * v / total_sum) for v in state_values]
            self.model[i] = parents_matrix[i] + state_values

        # Fill for no parents
        if len(self.parents) == 0:
            state_values = [random.random() for i in range(n_state_cols)]
            total_sum = sum(state_values)
            state_values = [str(100 * v / total_sum) for v in state_values]
            self.model[0] = state_values

        pass

    def validate_cpt(self):
        for line in self.model:
            svals = line[len(self.parents):]
            fvals = [float(s) for s in svals]
            if not sum(fvals) == 100.0:
                return False
        return True

    def get_cpt(self):
        cpt = []
        for line in self.model:
            svals = line[len(self.parents):]
            fvals = [float(s) for s in svals]
            cpt.append(fvals)
        return cpt


# class CellRendererClickablePixbuf(Gtk.CellRendererPixbuf):
#     g_signal('clicked', str)
#
#     def __init__(self):
#         Gtk.CellRendererPixbuf.__init__(self)
#         self.set_property('mode', gtk.CELL_RENDERER_MODE_ACTIVATABLE)
#
#     def do_activate(self, event, widget, path, background_area, cell_area, flags):
#         self.emit('clicked', path)