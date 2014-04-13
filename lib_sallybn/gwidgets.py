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


class GraphicCptTable:
    def __init__(self, vertices, edges, states, query_v, view=Gtk.TreeView()):
        """
        Create a tree view for the CPT of the node query_v
        :param vertices:
        :param edges:
        :param states:
        :param query_v:
        :return:
        """
        self.query_v = query_v
        self.states = states
        self.vertices = vertices
        self.edges = edges

        self.parents = None
        ### DATA MODEL
        self.model = None
        self.editable_cells = {}
        self.parents

        self.widget = self._create_treeview_for_cpt(view)

    def get_widget(self):
        return self.widget

    def _create_treeview_for_cpt(self, view):
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

        # data taypes for parents
        parent_types = [str for i in self.parents]
        # the data in the model (three strings for each row, one for each column)
        cpt_types = [str for i in self.states[self.query_v]]
        # all parent + cpt types
        all_types = parent_types + cpt_types

        print all_types

        ### DATA MODEL
        self.model = Gtk.ListStore(*all_types)
        view.set_model(self.model)

        # FILL DATA
        parents_matrix = util.parent_states(self.parents, self.states)
        state_values = ["0.0"] * n_state_cols

        for l in parents_matrix:
            self.model.append(l + state_values)

        # Fill for no parents
        if len(self.parents) == 0:
            self.model.append(state_values)


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

