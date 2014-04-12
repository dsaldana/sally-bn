### Graphic widgets

# Sally-BN
# Mavrin
# Johny Five
# Rose
# Bender
# Dorian

from gi.repository import Gtk
from gi.repository import Pango


import util


class GraphicCptTable:
    def __init__(self, vertices, edges, states, query_v):
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

        ### DATA MODEL
        self.model = None
        self.editable_cells = {}


        self.widget = self._create_treeview_for_cpt()

    def get_widget(self):
        return self.widget

    def _create_treeview_for_cpt(self):
        """
        Create a tree view for the CPT of the node query_v

        :return: a treeview widget
        """
        ### Detect parents
        parents = util.get_parents(self.query_v, self.edges)
    
        # numeric columns
        n_state_cols = len(self.states[self.query_v])
        # Columns for titles
        n_parent_cols = len(parents)
    
        # TODO Validate parents not zero states
        # number of rows
        n_rows = 1
        for p in parents:
            n_rows *= len(self.states[p])
    
        # data taypes for parents
        parent_types = [str for i in parents]
        # the data in the model (three strings for each row, one for each column)
        cpt_types = [str for i in self.states[self.query_v]]
        # all parent + cpt types
        all_types = parent_types + cpt_types
    
        print all_types
    
        ### DATA MODEL
        self.model = Gtk.ListStore(*all_types)
    
        # FILL DATA
        parents_matrix = util.parent_states(parents, self.states)
        state_values = ["0.0"] * n_state_cols

        for l in parents_matrix:
            self.model.append(l + state_values)
    
        view = Gtk.TreeView(self.model)
    
        # Table titles
        table_titles = parents + [s + "(%)" for s in self.states[self.query_v]]
    
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
    
            # append to the treeview
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