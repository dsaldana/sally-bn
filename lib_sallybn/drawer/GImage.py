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
import cairo as c


class GImage(GraphicObject):


    def __init__(self, gpoint_origin, name, png_file):
        self.file = png_file
        self.name = name
        self.origin = gpoint_origin

    def draw(self, cairo):
        img = c.ImageSurface.create_from_png(self.file)
        cairo.set_source_surface(img, 0, 0)
        # w = img.get_width()
        # h = img.get_width()
        cairo.paint()

    def is_on_point(self, p):
        pass