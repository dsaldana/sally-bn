import math

from lib_sallybn.drawer import color
from lib_sallybn.drawer.GraphicObject import GraphicObject
from lib_sallybn.drawer.color import yellow

DEFAULT_VERTEX_RADIO = 30.0


class GVertex(GraphicObject):
    """
    Graphic Vertex
    """

    def __init__(self, gpoint, name, color=None, vertex_radio=DEFAULT_VERTEX_RADIO):
        self.center = gpoint
        self.name = name
        self.vertex_radio = vertex_radio


    def is_on_point(self, p):
        """
        Evaluate if this vertex is on the point p
        :param p: point
        :param vertices: nodes
        :return: the vertex
        """
        x, y = self.center.x, self.center.y
        d = math.hypot(p[0] - x, p[1] - y)
        return  d < self.vertex_radio

    def draw(self, cairo):
        """
        Draw a vertex

        """
        vertex_radio = self.vertex_radio
        x, y = self.center.x, self.center.y

        ### Selected
        if self.selected:
            cairo.set_source_rgb(*yellow)  # yellow
            cairo.arc(x, y, vertex_radio + 5, 0, 2 * 3.1416)
            cairo.fill()

        ### Normal vertex
        ## Fill circle
        cairo.set_source_rgb(*color.light_blue)  # light blue
        cairo.arc(x, y, vertex_radio, 0, 2 * 3.1416)
        cairo.fill()

        ## Draw border
        cairo.set_source_rgb(*color.blue)  # blue
        cairo.arc(x, y, vertex_radio, 0, 2 * math.pi)
        cairo.stroke()

        ## Draw text
        text_position = vertex_radio + 15
        cairo.set_source_rgb(*color.dark_blue)  # blue
        # cairo.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cairo.select_font_face("Georgia")

        cairo.set_font_size(14)

        xbearing, ybearing, width, height, xadvance, yadvance = (
            cairo.text_extents(self.name))
        cairo.move_to(x + 0.5 - xbearing - width / 2,
                      y + text_position + 0.5 - ybearing - height / 2)
        cairo.show_text(self.name)


