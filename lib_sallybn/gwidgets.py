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
import math
from lib_sallybn.util import ulist



NEW_STATE_NAME = "-Click here for new state-"


class StatesTable:
    def __init__(self, disc_bn, selected_vetex,
                 state_changed_func, view, badd_state, bremove_state):

        """

        :param disc_bn:
        :param selected_vetex:
        :param state_changed_func:
        :param view:
        :param badd_state:
        :param bremove_state:
        """
        self.selected_vetex = selected_vetex
        self.disc_bn = disc_bn
        self.view = view
        self.state_changed_func = state_changed_func
        self.model = None
        self._modify_treeview_for_states()

        badd_state.connect("clicked", self._add_state)
        bremove_state.connect("clicked", self._remove_state)

    def _add_state(self, widget):
        self.model.append(["New state"])
        self.disc_bn.add_state(self.selected_vetex, "New state")
        self.state_changed_func()

    def _remove_state(self, widget):
        if len(self.model) != 0:
            (model, selected_rows) = self.view.get_selection().get_selected()
            if selected_rows is not None:
                del_state = self.model[selected_rows][0]
                # Graphic remove
                self.model.remove(selected_rows)
                # remove from graph
                self.disc_bn.add_state(self.selected_vetex, del_state)

    def _modify_treeview_for_states(self):
        ### MODEL
        self.model = Gtk.ListStore(str)
        self.view.set_model(self.model)

        states = self.disc_bn.get_states(self.selected_vetex)
        # fill states
        for state in states:
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

    def text_edited(self, widget, path, new_text):
        # Current name
        current_state = self.model[path][0]

        self.disc_bn.change_state_name(self.selected_vetex, current_state, new_text)
        # TODO validate non repeated names

        # modify gui
        self.model[path][0] = new_text
        self.state_changed_func()


class GraphicCptTable:
    def __init__(self, disc_bn, query_v, view):
        """
        Create a tree view for the CPT of the node query_v
        :param query_v:
        :return:
        """
        self.disc_bn = disc_bn

        self.view = view
        self.query_v = query_v

        ### DATA MODEL
        self.model = None
        self.editable_cells = {}
        # self.parents

        self.modify_treeview_for_cpt()

    def modify_treeview_for_cpt(self):
        """
        Modify a tree view for the CPT of the node query_v
        """
        ### Detect parents
        parents = self.disc_bn.getparents(self.query_v)

        node_states = self.disc_bn.get_states(self.query_v)
        # number of columns
        n_state_cols = len(node_states)
        # Columns for titles
        n_parent_cols = len(parents)

        # TODO Validate parents not zero states

        # number of rows
        n_rows = 1
        for p in parents:
            n_rows *= len(self.disc_bn.get_states(p))

        # data types for parents
        parent_types = [str for i in parents]
        # the data in the model (three strings for each row, one for each column)
        cpt_types = [str for i in node_states]
        # all parent + cpt types
        all_types = parent_types + cpt_types

        ### DATA MODEL
        self.model = Gtk.ListStore(*all_types)
        self.view.set_model(self.model)

        # FILL CLEAN CPT
        parents_matrix = self.disc_bn.get_parent_states(self.query_v)
        str_parent_matrix = self.disc_bn.str_parent_states(parents_matrix)
        cprob = self.disc_bn.get_cprob(self.query_v)

        # PUT CPT in model
        for l in range(n_rows):
            # Fill for no parents
            if len(parents) == 0:
                str_prob = ulist.list_to_str_list(cprob)
                print cprob
                self.model.append(str_prob)

            else:
                print l
                print str_parent_matrix[l]
                cprob_line = cprob[str_parent_matrix[l]]
                str_cprob_line = ulist.list_to_str_list(cprob_line)
                self.model.append(parents_matrix[l] + str_cprob_line)

        ### end fill data

        # Table titles
        table_titles = parents + [s + "(%)" for s in node_states]

        ### remove all columns
        cols = self.view.get_columns()
        for c in cols:
            self.view.remove_column(c)

        ####### ADD GRAPHIC COLUMNS
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
            self.view.append_column(col)


    ## Event for Edited cells
    def text_edited(self, widget, path, text):
        #2 validate the number between 0 and 100
        val = float(text)
        if val < 0 or val > 100:
            return
        #3 add the text
        col_number = self.editable_cells[widget]
        self.model[path][col_number] = text

    def fill_random(self):
        # number of  columns
        n_state_cols = len(self.disc_bn.get_states(self.query_v))

        # FILL DATA
        parents_matrix = self.disc_bn.get_parent_states(self.query_v)

        for i in range(len(parents_matrix)):
            state_values = [random.random() for j in range(n_state_cols)]
            total_sum = sum(state_values)
            state_values = [str(100 * v / total_sum) for v in state_values]
            self.model[i] = parents_matrix[i] + state_values

        # Fill for no parents
        if len(self.disc_bn.getparents(self.query_v)) == 0:
            state_values = [random.random() for i in range(n_state_cols)]
            total_sum = sum(state_values)
            state_values = [str(100 * v / total_sum) for v in state_values]
            self.model[0] = state_values


    def validate_cpt(self):
        for line in self.model:
            parents = self.disc_bn.getparents(self.query_v)
            svals = line[len(parents):]
            fvals = [float(s) for s in svals]
            # state values must sum 100 with precision of 0.001
            if not math.fabs(sum(fvals) - 100.0) < 0.001:
                return False
        return True

    # def get_cpt(self):
    #     cpt = []
    #     for line in self.model:
    #         svals = line[len(self.parents):]
    #         fvals = [float(s) for s in svals]
    #         cpt.append(fvals)
    #     return cpt

    def get_cprob_from_table(self):
        cprob = {}
        parents = self.disc_bn.getparents(self.query_v)

        for line in self.model:
            #key
            parent_states = line[:len(parents)]
            key = ulist.statelist_to_string(parent_states)
            # values
            svals = line[len(parents):]
            fvals = [float(s) for s in svals]

            if len(parents) == 0:
                return fvals
            else:
                cprob[key] = fvals

        print "from table:", cprob
        return cprob