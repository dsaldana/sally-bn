import math

from lib_sallybn.drawer.GArrow import GArrow
from lib_sallybn.drawer.GVertex import DEFAULT_VERTEX_RADIO


class GBoxArrow(GArrow):
    def __init__(self, box1, box2):
        self.p1 = box1.center
        self.p2 = box2.center

        self.box1 = box1
        self.box2 = box2
        self.headarrow_d = 0

        self.a_side = DEFAULT_VERTEX_RADIO / 1.5
        self.b_side = DEFAULT_VERTEX_RADIO / 4.0


    def draw(self, cairo):
        """

        :param cairo:
        """
        self._compute_headarrow()

        # Repaint arrow
        GArrow.draw(self, cairo)

    def _compute_headarrow(self):
        self.headarrow_d = math.hypot(self.p1.x - self.p2.x, self.p1.y - self.p2.y) / 2.0