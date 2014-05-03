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

from lib_sallybn.drawer.GraphicObject import GraphicObject

__author__ = 'dav'


class GRectangle(GraphicObject):
    """
    Graphic Vertex
    """
    def __init__(self, gpoint_origin, width, height, name):
        self.name = name
        self.width = width
        self.origin = gpoint_origin
        self.height = height

    def draw(self, cairo):
        # Fill rectangle
        cairo.set_source_rgb(*self.fill_color)
        cairo.rectangle(self.origin.x, self.origin.y, self.width, self.height)
        cairo.fill()
        # Border
        cairo.set_source_rgb(*self.border_color)
        cairo.rectangle(self.origin.x, self.origin.y, self.width, self.height)
        cairo.stroke()

        # Draw name
        if self.name is not None:
            cairo.set_source_rgb(*self.border_color)
            cairo.select_font_face("Georgia")
            #
            cairo.set_font_size(14)
            #
            xbearing, ybearing, width, height, xadvance, yadvance = (
                cairo.text_extents(self.name))
            cairo.move_to(self.origin.x + 0.5 - xbearing - width / 2.0 + self.width / 2.0,
                          self.origin.y - ybearing / 2.0 + height / 2.0 + self.height / 2.0)
            cairo.show_text(self.name)