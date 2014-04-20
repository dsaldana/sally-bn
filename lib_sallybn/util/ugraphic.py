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

import math
from random import shuffle
from gi.repository import Gtk

from lib_sallybn import GraphDrawer


def point_in_line(p, vertex_locations, edges):
    """
    Identify if a point is in one of the set of edges
    :param p point = [x,y]
    :param terminal points of the edges, is a dictionary {"v1":[x,y]}
    :param edges set of lines represented by two points each. ex [["v1","v2"],["v3","v2"]]
    """
    px, py = p

    for e in edges:
        x1, y1 = vertex_locations[e[0]]
        x2, y2 = vertex_locations[e[1]]

        # distance from p1 to p
        d1_p = math.hypot(x1 - px, y1 - py)
        # distance from p to p2
        d2_p = math.hypot(x2 - px, y2 - py)

        # distance prom p1 to p2
        d1_2 = math.hypot(x2 - x1, y2 - y1)

        # validate
        if d1_p + d2_p - d1_2 < 0.5:
            return e

    return None


def point_in_circle(p, vertices):
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


def create_widget(glade_file, widget_names, handler=None):
    """
    Create a widget from a glade file
    :glade_file
    """
    # GTK builder
    builder = Gtk.Builder()
    builder.add_from_file(glade_file)

    if handler is not None:
        builder.connect_signals(handler)

    return [builder.get_object(wname) for wname in widget_names]


def create_vertex_locations(graph_skeleton, dx=220, dy=180):
    """
    Organize the graph in order to show it.
    """
    vertex = list(graph_skeleton.get_vertices())

    ## Extract root nodes
    roots = []
    for v in vertex:
        if len(graph_skeleton.getparents(v)) == 0:
            roots.append(v)

    ## Bread first search for each node
    # Initinal distances
    dist = {r: 0 for r in roots}
    level = {0: list(roots)}
    # maintain a queue of paths
    # push the roots into the queue
    queue = roots

    # random order for roots
    shuffle(queue)

    while queue:
        # get the first path from the queue
        parent = queue.pop(0)
        children = graph_skeleton.getchildren(parent)

        for child in children:
            if child in vertex:
                lev = dist[parent] + 1
                dist[child] = lev

                # add level
                if not lev in level:
                    level[lev] = []
                # add child to level
                if not child in level[lev]:
                    level[lev].append(child)

                queue.append(child)
                vertex.remove(child)

    max_level = max([len(level[k]) for k in level.keys()])

    max_width = (max_level + 2) * dx

    vertex_locations = {}

    # for each level
    for lk in level.keys():
        lvertices = level[lk]
        shuffle(lvertices)
        len_level = len(lvertices)
        for i in range(len_level):
            #vertex pos
            x = (i + 1) * max_width / (len_level + 1)
            y = (lk + 1) * dy

            vertex_locations[lvertices[i]] = [x, y]

    return vertex_locations


def show_warning(window, message, sec_text=""):
    dialog = Gtk.MessageDialog(window, 0, Gtk.MessageType.WARNING,
                               Gtk.ButtonsType.OK, message)
    dialog.set_title("Warning")
    dialog.format_secondary_text(sec_text)
    dialog.run()
    dialog.destroy()

