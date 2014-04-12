### Graphic widgets

# Sally-BN
# Mavrin
# Johny Five
# Rose
# Bender
# Dorian

from gi.repository import Gtk
from gi.repository import Pango





class CptTable(Gtk.ApplicationWindow):
    def __init__(self, app, vertices, edges, states, query_v):
        Gtk.Window.__init__(self, title="CPT for " + query_v, application=app)
        self.set_default_size(250, 100)
        self.set_border_width(10)

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
        rows = 1
        for p in parents:
            rows *= len(states[p])
        print parents, "-", states[query_v]

        # data taypes for parents
        parent_types = [str for i in parents]
        # the data in the model (three strings for each row, one for each column)
        cpt_types = [str for i in states[query_v]]
        # all parent + cpt types
        all_types = parent_types + cpt_types

        print all_types
        # cpt_models[1].append(["x"])

        model = Gtk.ListStore(*all_types)
        model.append(["x", "y", str(1.0), str(2.0)])


        view = Gtk.TreeView(model)

        # Table titles
        table_titles = parents + [s + "(%)" for s in states[query_v]]

        editable_cells = {}
        # for each column
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

                def edited_cb(cell, path, new_text, user_data):
                    print "edited aa"

                editable_cells[cell] = i

                ## Event for Edited cells
                def text_edited(widget, path, text):
                    #1 remove the % symbol and spaces
                    # text = text.replace("%","")
                    # text = text.replace(" ","")
                    print text
                    #2 validate the number between 0 and 100
                    val = float(text)
                    if val < 0 or val >100:
                        return
                    #3 add the text
                    # text = str(val) + "%"
                    col_number = editable_cells[widget]
                    model[path][col_number] = text

                # Call signal
                cell.connect("edited", text_edited)

            # the column is created
            col = Gtk.TreeViewColumn(table_titles[i], cell, text=i)

            # append to the treeview
            view.append_column(col)


        # FILL the table

        # when a row is selected, it emits a signal
        # view.get_selection().connect("changed", self.on_changed)

        # the label we use to show the selection
        self.label = Gtk.Label()
        self.label.set_text("fads")

        # a grid to attach the widgets
        grid = Gtk.Grid()
        grid.attach(view, 0, 0, 1, 1)
        grid.attach(self.label, 0, 1, 1, 1)

        # attach the grid to the window
        self.add(grid)

    def on_changed(self, selection):
        # get the model and the iterator that points at the data in the model
        (model, iter) = selection.get_selected()
        # set the label to a new value depending on the selection
        self.label.set_text("\n %s %s %s" % (model[iter][0], model[iter][1], model[iter][2]))
        print "changed"
        return True


