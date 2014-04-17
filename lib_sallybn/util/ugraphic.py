import math
from lib_sallybn import GraphDrawer
from gi.repository import Gtk, Gdk




# MOVE TO tuils
def vertex_in_circle(p, vertices):
    """
    Serach if there is a node in the clicked point

    :param p: point
    :param vertices: nodes
    :return: the vertex
    """
    radious = GraphDrawer.vertex_radious
    vertex = None
    for k, point in vertices.items():
        if math.hypot(p[0] - point[0], p[1] - point[1]) < radious:
            vertex = k
            break

    return vertex

def create_widget(glade_file, *widget_names):
    # GTK builder
    builder = Gtk.Builder()
    builder.add_from_file(glade_file)

    return [builder.get_object(wname) for wname in widget_names]