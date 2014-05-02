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

from lib_sallybn.drawer import color
from lib_sallybn.drawer.GraphicObject import GraphicObject
from lib_sallybn.drawer.color import yellow

DEFAULT_VERTEX_RADIO = 30.0


class GVertex(GraphicObject):
    """
    Graphic Vertex
    """

    def __init__(self, gpoint, name, vertex_radio=DEFAULT_VERTEX_RADIO):
        self.center = gpoint
        self.name = name
        self.vertex_radio = vertex_radio

        self.border_color = color.blue
        self.fill_color = color.light_blue
        self.text_color = color.dark_blue

    def is_on_point(self, p):
        """
        Evaluate if this vertex is on the point p
        :param p: point
        :param vertices: nodes
        :return: the vertex
        """
        x, y = self.center.x, self.center.y
        d = math.hypot(p[0] - x, p[1] - y)
        return d < self.vertex_radio

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
        cairo.set_source_rgb(*self.fill_color)  # light blue
        cairo.arc(x, y, vertex_radio, 0, 2 * 3.1416)
        cairo.fill()

        ## Draw border
        cairo.set_source_rgb(*self.border_color)  # blue
        cairo.arc(x, y, vertex_radio, 0, 2 * math.pi)
        cairo.stroke()

        ## Draw text
        text_position = vertex_radio + 15
        cairo.set_source_rgb(*self.text_color)  # blue
        # cairo.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cairo.select_font_face("Georgia")

        cairo.set_font_size(14)

        xbearing, ybearing, width, height, xadvance, yadvance = (
            cairo.text_extents(self.name))
        cairo.move_to(x + 0.5 - xbearing - width / 2,
                      y + text_position + 0.5 - ybearing - height / 2)
        cairo.show_text(self.name)


