from lib_sallybn.drawer.GPoint import GPoint
from lib_sallybn.drawer.GraphicObject import GraphicObject
from lib_sallybn.drawer.color import gray, light_green, light_gray, green, dark_green, \
    white

box_width = 160
delta_state = 30
title_height = delta_state + 5


class GStateBox(GraphicObject, GPoint):

    def __init__(self, center, name, marginals, evidence):
        """
          :param vertex_locations dic with name and point, ex. {"v1":[x,y]}
        :param marginals dic with marginal probabilities to all variables
            ex. {"v1":{"state1": 0.5, "state2": 0.5}}
        :param evidence is a dictionary with vertex name and state {"vertex_name":"state"}
        """
        self.x, self.y = center
        self.marginals = marginals
        self.evidence = evidence
        self.name = name
        self.selected_state = None

    def draw(self, cairo):
        """
        Draw boxes for each variable with its marginal probabilities.
        :param cairo to draw

        """
        marginals = self.marginals
        vname = self.name
        evidence = self.evidence

        v_states = marginals.keys()
        is_evidence = vname in evidence
        # Rectangles
        px, py = self.x, self.y
        box_heigh = self.get_box_height(v_states)
        x_corner = px - box_width / 2.0
        y_corner = py - box_heigh / 2.0

        #Background for evidence
        if is_evidence:
            cairo.set_source_rgb(*gray)
            cairo.rectangle(x_corner - 3, y_corner - 3, box_width + 6, box_heigh + 6)
            cairo.fill()

        # Background
        cairo.set_source_rgb(*light_green)  # light green

        ## if is evidence
        if is_evidence:
            cairo.set_source_rgb(*light_gray)  # light gray

        cairo.rectangle(x_corner, y_corner, box_width, box_heigh)
        cairo.fill()

        # Title background
        cairo.set_source_rgb(*green)  # green
        cairo.rectangle(x_corner, y_corner, box_width, title_height)
        cairo.fill()

        ## Title text
        cairo.select_font_face("Georgia")
        cairo.set_source_rgb(*dark_green)  # dark green
        cairo.move_to(x_corner + 5, y_corner + 25)
        cairo.set_font_size(17)
        cairo.show_text(vname)

        # Background rectangle for prob value box
        rwidth = (box_width / 2 - 10)
        rheight = delta_state / 2.0 + 5.0

        # For each state
        for i in range(len(v_states)):
            ny = y_corner + title_height + (i + 1) * delta_state

            # Text for states
            cairo.select_font_face("Georgia")
            cairo.set_source_rgb(15.0 / 255, 158.0 / 255, 0.0 / 255)
            cairo.set_font_size(14)
            cairo.move_to(x_corner + 5, ny - 10)
            cairo.show_text(v_states[i][:11])

            ### Values
            rx = x_corner + box_width / 2.0
            ry = ny - 25.0

            # Prob rectangle
            cairo.set_source_rgb(*gray)  # gray
            cairo.rectangle(rx, ry, rwidth, rheight)
            cairo.fill()

            val = marginals[v_states[i]]
            # Prob rectangle
            val_width = rwidth * val
            cairo.set_source_rgb(*dark_green)  # dark green
            cairo.rectangle(rx, ry, val_width, rheight)
            cairo.fill()

            # Text for value
            cairo.select_font_face("Georgia")
            cairo.set_source_rgb(*white)
            cairo.set_font_size(14)
            cairo.move_to(rx + 5, ny - 10)
            cairo.show_text(str(val * 100)[:5] + "")

            ## State line
            cairo.set_line_width(0.5)
            cairo.set_source_rgb(*green)  # green
            cairo.move_to(x_corner, ny)
            cairo.line_to(x_corner + box_width, ny)
            cairo.stroke()

        #Border
        cairo.set_line_width(0.5)
        cairo.set_source_rgb(*dark_green)
        cairo.rectangle(x_corner, y_corner, box_width, box_heigh)
        cairo.stroke()

        # Line title
        cairo.move_to(x_corner, y_corner + title_height)
        cairo.line_to(x_corner + box_width, y_corner + title_height)
        cairo.stroke()

    def is_on_point(self, p):
        """
        :p point to evaluate [x,y]
        :param vertex_locations dic with name and point, ex. {"v1":[x,y]}
        :param marginals dic with marginal probabilities to all variables
            ex. {"v1":{"state1": 0.5, "state2": 0.5}}
        :return: ("vertex", "state")
        """
        x, y = p

        # states of vertex
        v_states = self.marginals.keys()
        box_heigh = GStateBox.get_box_height(v_states)

        # go to left-upper corner
        x_corner = self.x - box_width / 2.0
        y_corner = self.y - box_heigh / 2.0

        #if point.x is not in range
        if not x_corner < x <= x_corner + box_width:
            return False

        #if title


        # evaluate each state for p.y
        for i in range(len(v_states)):
            ny = y_corner + title_height + i * delta_state
            ny_next = y_corner + title_height + (i + 1) * delta_state

            if ny < y <= ny_next:
                self.selected_state = v_states[i]
                return True
        return False

    @staticmethod
    def get_box_height(num_states):
        return title_height + delta_state * len(num_states)