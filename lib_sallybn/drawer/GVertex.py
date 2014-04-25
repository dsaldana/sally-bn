import math

from lib_sallybn.drawer import color
from lib_sallybn.drawer.GraphicObject import GraphicObject
from lib_sallybn.drawer.color import yellow

DEFAULT_VERTEX_RADIO = 30.0


class GVertex(GraphicObject):
    """
    Graphic Vertex
    """

    def __init__(self, center, name, color=None, vertex_radio=DEFAULT_VERTEX_RADIO):
        self.c = center
        self.vname = name
        self.selected = False
        self.vertex_radio = vertex_radio

    def set_selected(self, val):
        self.selected = val

    def is_on_point(self, p):
        """
        Evaluate if this vertex is on the point p
        :param p: point
        :param vertices: nodes
        :return: the vertex
        """
        return math.hypot(p[0] - self.c[0], p[1] - self.c[1]) < self.vertex_radio


    def draw(self, cairo):
        """
        Draw a vertex

        """
        vertex_radio  = self.vertex_radio

        ### Selected
        if self.selected:
            point = self.c
            cairo.set_source_rgb(*yellow)  # yellow
            cairo.arc(point[0], point[1], vertex_radio + 5, 0, 2 * 3.1416)
            cairo.fill()

        ### Normal vertex
        ## Fill circle
        cairo.set_source_rgb(*color.light_blue)  # light blue
        cairo.arc(self.c[0], self.c[1], vertex_radio, 0, 2 * 3.1416)
        cairo.fill()

        ## Draw border
        cairo.set_source_rgb(*color.blue)  # blue
        cairo.arc(self.c[0], self.c[1], vertex_radio, 0, 2 * math.pi)
        cairo.stroke()

        ## Draw text
        text_position = vertex_radio + 15
        cairo.set_source_rgb(*color.dark_blue)  # blue
        # cairo.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cairo.select_font_face("Georgia")

        cairo.set_font_size(14)

        xbearing, ybearing, width, height, xadvance, yadvance = (
            cairo.text_extents(self.vname))
        cairo.move_to(self.c[0] + 0.5 - xbearing - width / 2,
                      self.c[1] + text_position + 0.5 - ybearing - height / 2)
        cairo.show_text(self.vname)


