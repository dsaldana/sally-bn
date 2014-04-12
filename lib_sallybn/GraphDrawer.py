import math

# Node radious
vertex_radious = 30.0

box_width = 100
delta_state = 30
title_height = delta_state + 5


class GraphDrawer:
    def __init__(self, area):
        self.area = area
        self.transform = None


    def draw_background(self, cairo):
        cairo.set_source_rgb(1, 1, 1.0)
        # FIXME only white for the workspace.
        #self.area.size_request().width
        #self.area.size_request().height
        cairo.rectangle(0, 0, 10000, 100000)
        cairo.fill()

    def draw_directed_arrows(self, cairo, edges, vertices, headarrow_d =vertex_radious):
        for edge in edges:
            x1, y1 = vertices[edge[0]]
            x2, y2 = vertices[edge[1]]
            dx, dy = float(x2 - x1), float(y2 - y1)

            cairo.set_source_rgb(0, 0, 0.0)
            cairo.move_to(x1, y1)
            cairo.line_to(x2, y2)
            cairo.stroke()

            #draw arrow
            d = math.hypot(dx, dy) - headarrow_d
            theta = math.atan(dy / dx)
            # adjust for atan
            s = 1.0
            if dx < 0:
                s = -1.0

            # arrow head (triangle)
            a = vertex_radious / 2.0
            b = vertex_radious / 3.5

            xt1 = x1 + s * d * math.cos(theta)
            yt1 = y1 + s * d * math.sin(theta)

            xt2 = x1 + s * (d - a) * math.cos(theta) - s * b * math.sin(theta)
            yt2 = y1 + s * (d - a) * math.sin(theta) + s * b * math.cos(theta)

            b = -b
            xt3 = x1 + s * (d - a) * math.cos(theta) - s * b * math.sin(theta)
            yt3 = y1 + s * (d - a) * math.sin(theta) + s * b * math.cos(theta)

            cairo.move_to(xt1, yt1)
            cairo.line_to(xt2, yt2)
            cairo.line_to(xt3, yt3)
            cairo.line_to(xt1, yt1)

            cairo.fill()

    def draw_selected_vertices(self, cairo, selected_vertex, vertices):
        ## selected node
        point = vertices[selected_vertex]
        cairo.set_source_rgb(1, 0.8, 0.0)  # yellow
        cairo.arc(point[0], point[1], vertex_radious + 5, 0, 2 * 3.1416)
        cairo.fill()


    def draw_vertices(self, cairo, vertices):
        for vname, point in vertices.items():
            ## Fill circle
            cairo.set_source_rgb(0.61, 0.75, 1.0)  # light blue
            cairo.arc(point[0], point[1], vertex_radious, 0, 2 * 3.1416)
            cairo.fill()

            ## Draw border
            cairo.set_source_rgb(0.22, 0.30, 0.66)  # blue
            cairo.arc(point[0], point[1], vertex_radious, 0, 2 * 3.1416)
            cairo.stroke()

            ## Draw text
            text_position = vertex_radious + 15
            cairo.set_source_rgb(0.12, 0.20, 0.56)  # blue
            # cairo.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            cairo.select_font_face("Georgia");

            cairo.set_font_size(14)

            xbearing, ybearing, width, height, xadvance, yadvance = (
                cairo.text_extents(vname))
            cairo.move_to(point[0] + 0.5 - xbearing - width / 2,
                          point[1] + text_position + 0.5 - ybearing - height / 2)
            cairo.show_text(vname)


    def draw_arrow_box(self, cairo, vertices, edges):
        for edge in edges:
            x1, y1 = vertices[edge[0]]
            x2, y2 = vertices[edge[1]]
            dx, dy = float(x2 - x1), float(y2 - y1)

            cairo.set_source_rgb(0, 0, 0.0)
            cairo.move_to(x1, y1)
            cairo.line_to(x2, y2)
            cairo.stroke()

            #draw arrow
            # FIXME put the headarrow in the right place
            d = math.hypot(dx, dy)/2
            theta = math.atan(dy / dx)
            # adjust for atan
            s = 1.0
            if dx < 0:
                s = -1.0

            # arrow head (triangle)
            a = vertex_radious / 2.0
            b = vertex_radious / 3.5

            xt1 = x1 + s * d * math.cos(theta)
            yt1 = y1 + s * d * math.sin(theta)

            xt2 = x1 + s * (d - a) * math.cos(theta) - s * b * math.sin(theta)
            yt2 = y1 + s * (d - a) * math.sin(theta) + s * b * math.cos(theta)

            b = -b
            xt3 = x1 + s * (d - a) * math.cos(theta) - s * b * math.sin(theta)
            yt3 = y1 + s * (d - a) * math.sin(theta) + s * b * math.cos(theta)

            cairo.move_to(xt1, yt1)
            cairo.line_to(xt2, yt2)
            cairo.line_to(xt3, yt3)
            cairo.line_to(xt1, yt1)

            cairo.fill()

    def draw_boxes(self, cairo, vertices, states):
        for vname, point in vertices.items():
            # Rectangles
            px, py = point

            box_heigh = self._get_box_height(states)

            x_corner = px - box_width / 2.0
            y_corner = py - box_heigh / 2.0

            # Background
            cairo.set_source_rgb(230.0 / 255, 242.0 / 255, 230.0 / 255)  # light green
            cairo.rectangle(x_corner, y_corner, box_width, box_heigh)
            cairo.fill()

            # Border
            cairo.set_source_rgb(204.0 / 255, 229.0 / 255, 204.0 / 255)  # green
            cairo.rectangle(x_corner, y_corner, box_width, title_height)
            cairo.fill()

            ## Title
            cairo.select_font_face("Georgia")
            cairo.set_source_rgb(59.0 / 255, 143.0 / 255, 0.0 / 255)  # dark green
            # cairo.set_source_rgb(0.0 / 255, 0.0 / 255, 0.0 / 255)  # green
            cairo.move_to(x_corner + 5, y_corner + 25)
            cairo.set_font_size(17)
            cairo.show_text(vname)

            for i in range(len(states)):
                ## States
                ny = y_corner + title_height + (i + 1) * delta_state
                cairo.set_source_rgb(204.0 / 255, 229.0 / 255, 204.0 / 255)  # green
                cairo.move_to(x_corner, ny)
                cairo.line_to(x_corner + box_width, ny)
                cairo.stroke()

                # Text for states
                cairo.select_font_face("Georgia")
                cairo.set_source_rgb(69.0 / 255, 163.0 / 255, 0.0 / 255)  # dark green
                cairo.set_font_size(14)
                cairo.move_to(x_corner + 5, ny - 10)
                cairo.show_text(states[i])

    @staticmethod
    def _get_box_height(states):
        return title_height + delta_state * len(states)

