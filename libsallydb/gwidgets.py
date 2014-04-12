### Graphic widgets

# Sally-BN
# Mavrin
# Johny Five
# Rose
# Bender
# Dorian

from gi.repository import Gtk
from gi.repository import Pango


def parets_states(parents, states):
    """

    :param parents: list of parent names
    :param states: disctionary with k=vertex names and v=list of states
    """
    parents_matrix = []
    for par in parents:
        p_sts = states[par]

        if not parents_matrix:
            parents_matrix = [[s] for s in p_sts]
        else:
            new_par_matrix = []
            # previous parents
            for prev_p in parents_matrix:
                for pstate in p_sts:
                    tmp = list(prev_p)
                    tmp.append(pstate)
                    new_par_matrix.append(tmp)

            parents_matrix = new_par_matrix
    return parents_matrix


def create_treeview_for_cpt(vertices, edges, states, query_v):
    """
    Create a tree view for the CPT of the node query_v
    :param vertices:
    :param edges:
    :param states:
    :param query_v:
    :return:
    """
    ### Detect parents
    parents = []
    for v1, v2 in edges:
        if v2 == query_v:
            parents.append(v1)

    # numeric columns
    n_state_cols = len(states[query_v])
    # Columns for titles
    n_parent_cols = len(parents)

    # TODO Validate parents not zero states
    # number of rows
    n_rows = 1
    for p in parents:
        n_rows *= len(states[p])

    # data taypes for parents
    parent_types = [str for i in parents]
    # the data in the model (three strings for each row, one for each column)
    cpt_types = [str for i in states[query_v]]
    # all parent + cpt types
    all_types = parent_types + cpt_types

    print all_types

    ### DATA MODEL
    model = Gtk.ListStore(*all_types)

    # FILL DATA
    parents_matrix = parets_states(parents, states)
    state_vals = ["0.0"] * n_state_cols

    print "result="
    for l in parents_matrix:
        model.append(l + state_vals)

    # self.set_model = model
    view = Gtk.TreeView(model)

    # Table titles
    table_titles = parents + [s + "(%)" for s in states[query_v]]

    editable_cells = {}

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
            editable_cells[cell] = i
            ## Event for Edited cells
            def text_edited(widget, path, text):
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
                col_number = editable_cells[widget]
                model[path][col_number] = text

            # Call signal
            cell.connect("edited", text_edited)

        print editable_cells
        # the column is created
        col = Gtk.TreeViewColumn(table_titles[i], cell, text=i)

        # append to the treeview
        view.append_column(col)

    return view