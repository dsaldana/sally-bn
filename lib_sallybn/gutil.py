import math
from lib_sallybn import GraphDrawer

__author__ = 'dav'


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