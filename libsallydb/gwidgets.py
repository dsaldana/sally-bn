### Graphic widgets

# Sally-BN
# Mavrin
# Johny Five
# Rose
# Bender
# Dorian

from gi.repository import Gtk
from gi.repository import Pango


columns = ["First Name",
           "Last Name",
           "Phone Number"]

phonebook = [["Jurg", "Billeter", "555-0123"],
             ["Johannes", "Schmid", "555-1234"],
             ["Julita", "Inca", "555-2345"],
             ["Javier", "Jardon", "555-3456"],
             ["Jason", "Clinton", "555-4567"],
             ["Random J.", "Hacker", "555-5678"]]


def inIta(col, cell, model, iter, mymodel):
    s = model.get_string_from_iter(iter)
    niter = mymodel.get_iter_from_string(s)
    obj = mymodel.get_value(niter, 0)
    cell.set_property('text', obj)


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
        n_cols = len(states[query_v])
        # Columns for titles
        title_cols = len(parents)

        # TODO Validate parents not zero states
        # number of rows
        rows = len(states[query_v])
        for p in parents:
            rows *= len(states[p])
        print parents, "-", states[query_v]

        # the data in the model (three strings for each row, one for each column)
        cpt_models = [Gtk.ListStore(str) for i in states[query_v]]
        #FIXME other gtype non editable
        parent_models = [Gtk.ListStore(str) for i in parents]
        all_models = cpt_models + parent_models

        # all_models[0].append(["x"])
        for a in all_models:
            a.append(["x"])
        #
        # for a in all_models:
        #     a.append(["y"])
        #
        # for a in all_models:
        #     a.append(["z"])

        # append the values in the model
        # for i in range(len(phonebook)):
        #     listmodel.append(phonebook[i])

        # a treeview to see the data stored in the model
        # cpt_views = [Gtk.TreeView(model=mod) for mod in cpt_models]
        # parent_views = [Gtk.TreeView(model=mod) for mod in parent_models]
        # all_views = cpt_views + parent_views
        view = Gtk.TreeView(all_models[0])

        # Table titles
        table_titles = parents + states[query_v];

        # for each column
        for i in range(len(table_titles)):
            # cellrenderer to render the text
            cell = Gtk.CellRendererText()
            cell.set_property("editable", True)

            # Title in bold
            if i == 0:
                cell.props.weight_set = True
                cell.props.weight = Pango.Weight.BOLD

            # the column is created
            col = Gtk.TreeViewColumn(table_titles[i], cell, text=i)

            # and it is appended to the treeview
            view.append_column(col)



        # FILL the table









        # when a row is selected, it emits a signal
        view.get_selection().connect("changed", self.on_changed)

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
        return True

