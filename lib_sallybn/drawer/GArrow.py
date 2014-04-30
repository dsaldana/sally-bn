import math

from lib_sallybn.drawer.GVertex import DEFAULT_VERTEX_RADIO
from lib_sallybn.drawer.GraphicObject import GraphicObject


SELECT_TOLERANCE = 0.5


class GArrow(GraphicObject):
    """
    Graphic Vertex
    """
    def __init__(self, p1, p2, headarrow_d=DEFAULT_VERTEX_RADIO):
        """
        :p1: initial point GPoint
        :p2: final point GPoint
        :head_distance: distance of the head
        """
        self.p1 = p1
        self.p2 = p2

        self.headarrow_d = headarrow_d

        self.a_side = DEFAULT_VERTEX_RADIO / 2.5
        self.b_side = DEFAULT_VERTEX_RADIO / 5.0

    def is_on_point(self, p):
        """
         Identify if  the arrow is on the point p
         :param p point = [x,y]
        """
        px, py = p

        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y

        # distance from p1 to p
        d1_p = math.hypot(x1 - px, y1 - py)
        # distance from p to p2
        d2_p = math.hypot(x2 - px, y2 - py)

        # distance prom p1 to p2
        d1_2 = math.hypot(x2 - x1, y2 - y1)

        # validate, if it is near
        return d1_p + d2_p - d1_2 < SELECT_TOLERANCE

    def draw(self, cairo):
        """
        Draw arrow
        """
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y

        # selected arrow
        if self.selected:
            cairo.set_source_rgb(244 / 255.0, 192 / 255.0, 125 / 255.0)
            cairo.set_line_width(9.1)
            cairo.move_to(x1, y1)
            cairo.line_to(x2, y2)
            cairo.stroke()
            cairo.set_line_width(2.0)

        dx, dy = float(x2 - x1), float(y2 - y1)

        # Avoid problem with atan
        if dx == 0:
            dx = 1

        cairo.set_source_rgb(0, 0, 0.0)

        #draw arrow
        d = math.hypot(dx, dy) - self.headarrow_d
        theta = math.atan(dy / dx)
        # adjust for atan
        s = 1.0
        if dx < 0:
            s = -1.0

        # arrow head (triangle)
        a = self.a_side
        b = self.b_side
        # Final point
        xf = x1 + s * d * math.cos(theta)
        yf = y1 + s * d * math.sin(theta)

        xt2 = x1 + s * (d - a) * math.cos(theta) - s * b * math.sin(theta)
        yt2 = y1 + s * (d - a) * math.sin(theta) + s * b * math.cos(theta)

        b = -b
        xt3 = x1 + s * (d - a) * math.cos(theta) - s * b * math.sin(theta)
        yt3 = y1 + s * (d - a) * math.sin(theta) + s * b * math.cos(theta)

        cairo.move_to(xf, yf)
        cairo.line_to(xt2, yt2)
        cairo.line_to(xt3, yt3)
        cairo.line_to(xf, yf)
        cairo.fill()

        # initial point
        xi = x1 + s * DEFAULT_VERTEX_RADIO * math.cos(theta)
        yi = y1 + s * DEFAULT_VERTEX_RADIO * math.sin(theta)
        # Final point
        # xf = x1 + s * (d - 2) * math.cos(theta)
        # yf = y1 + s * (d - 2) * math.sin(theta)

        cairo.move_to(xi, yi)
        cairo.line_to(x2, y2)
        cairo.stroke()