


from gi.repository import Gtk, Gdk
import math

from enum import Enum

# vertex radio
rad = 30.0

# Mode for
class Mode(Enum):
    edit = 0
    run = 1


# Mode for edition
class ModeEdit(Enum):
    manual = 0
    vertex = 1
    edge = 2
    delete = 3





class AreaDrawer:

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





class Handler:
    def __init__(self, area):
        # Scale
        self.drawer = AreaDrawer(area)
        self.area = area
        self.scale = 1
        self.delta_zoom = 0.1
        self.mode_edit = ModeEdit.vertex
        self.mode = Mode.edit

        # Temporal vertex for edge
        self.vertex_1 = None
        self.vertex_2 = None
        self.vertex_count = 1

        # Graph
        self.vertex = {}
        self.edges = []


        #FIXME change all events for only motion
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.SCROLL_MASK |
                             Gdk.EventMask.SMOOTH_SCROLL_MASK | Gdk.EventMask.ALL_EVENTS_MASK)
        self.area.connect('draw', self.on_drawing_area_draw)

        self.area.connect("motion_notify_event", self.motion_event)
        self.area.connect('button-press-event', self.on_drawing_area_button_press)
        self.area.connect('scroll-event', self.on_scroll)
        self.clicks = []
        self.transform = None
        self.trans_point = None


    def on_scroll(self, widget, event):
        #print event.direction, event.delta_x, event.delta_y
        self.trans_point = [event.x, event.y]
        self.scale -= self.delta_zoom * event.delta_y

        self.area.queue_draw()
        return True


    def on_drawing_area_button_press(self, widget, event):
        p = [event.x, event.y]
        if self.transform is not None:
            p = self.transform.transform_point(event.x, event.y)

        #### Mode Edit #####
        if self.mode == Mode.edit:
            self.vertex_2 = None
            # search if a node exist in that point
            for k, point in self.vertex.items():
                if math.hypot(p[0] - point[0], p[1] - point[1]) < rad:
                    self.vertex_2 = k

            ## Mode
            if self.mode_edit == ModeEdit.vertex:
                if self.vertex_2 is None:
                    vname = 'Variable ' + str(self.vertex_count)
                    self.vertex[vname] = p
                    self.vertex_count += 1

            elif self.mode_edit == ModeEdit.edge:
                # If there is not a initial vertex selected
                if self.vertex_1 is None:
                    self.vertex_1 = self.vertex_2
                else:
                    if not self.vertex_1 == self.vertex_2 and self.vertex_2 is not None:
                        self.edges.append([self.vertex_1, self.vertex_2])
                        self.vertex_1 = None
                        print "New Edge"
            elif self.mode_edit == ModeEdit.delete:
                # Delete vertex
                self.vertex.pop(self.vertex_2)
                # delete edges
                for [v1, v2] in self.edges:
                    if v1 == self.vertex_2 or v2 == self.vertex_2:
                        self.edges.remove([v1, v2])

        ##### Mode run
        elif self.mode == Mode.run:
            pass

        self.area.queue_draw()
        return True

    def on_drawing_area_draw(self, drawing_area, cairo):
        cairo.scale(self.scale, self.scale)

        # TODO translate for zoom
        # if self.trans_point is not None:
        #     tx, ty = self.transform.transform_point(self.trans_point[0], self.trans_point[1])
        #     cairo.translate(tx, ty)

        self.transform = cairo.get_matrix()
        self.transform.invert()


        self.drawer.draw_background(cairo)



        if self.mode == Mode.edit:
            # Draw edges
            for edge in self.edges:
                x1, y1 = self.vertex[edge[0]]
                x2, y2 = self.vertex[edge[1]]
                dx, dy = float(x2 - x1), float(y2 - y1)

                cairo.set_source_rgb(0, 0, 0.0)
                cairo.move_to(x1, y1)
                cairo.line_to(x2, y2)
                cairo.stroke()

                #draw arrow
                d = math.hypot(dx, dy) - rad
                theta = math.atan(dy / dx)
                # adjust for atan
                s = 1.0
                if dx < 0:
                    s = -1.0

                # arrow head (triangle)
                a = rad / 2.0
                b = rad / 3.5

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

            # Draw nodes
            for vname, point in self.vertex.items():
                ## selected node
                if self.vertex_1 is not None and self.vertex_1 == vname:
                    cairo.set_source_rgb(1, 0.8, 0.0)  # yellow
                    cairo.arc(point[0], point[1], rad + 5, 0, 2 * 3.1416)
                    cairo.fill()

                ## Fill circle
                cairo.set_source_rgb(0.61, 0.75, 1.0)  # light blue
                cairo.arc(point[0], point[1], rad, 0, 2 * 3.1416)
                cairo.fill()

                ## Draw border
                cairo.set_source_rgb(0.22, 0.30, 0.66)  # blue
                cairo.arc(point[0], point[1], rad, 0, 2 * 3.1416)
                cairo.stroke()

                ## Draw text
                text_position = rad + 15
                cairo.set_source_rgb(0.12, 0.20, 0.56)  # blue
                # cairo.select_font_face("Georgia", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cairo.select_font_face("Georgia");

                cairo.set_font_size(14)

                xbearing, ybearing, width, height, xadvance, yadvance = (
                    cairo.text_extents(vname))
                cairo.move_to(point[0] + 0.5 - xbearing - width / 2,
                              point[1] + text_position + 0.5 - ybearing - height / 2)
                cairo.show_text(vname)

        elif self.mode == Mode.run:
            # Draw edges
            for edge in self.edges:
                x1, y1 = self.vertex[edge[0]]
                x2, y2 = self.vertex[edge[1]]
                dx, dy = float(x2 - x1), float(y2 - y1)

                cairo.set_source_rgb(0, 0, 0.0)
                cairo.move_to(x1, y1)
                cairo.line_to(x2, y2)
                cairo.stroke()

                #draw arrow
                d = math.hypot(dx, dy)
                theta = math.atan(dy / dx)
                # adjust for atan
                s = 1.0
                if dx < 0:
                    s = -1.0

                # arrow head (triangle)
                a = rad / 2.0
                b = rad / 3.5

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

            # Draw nodes
            for vname, point in self.vertex.items():
                # Rectangles
                px, py = point

                states = ["true", "false"]

                box_width = 100
                delta_state = 30
                title_heigh = delta_state + 5
                box_heigh = title_heigh + delta_state * len(states)

                cairo.set_source_rgb(230.0 / 255, 242.0 / 255, 230.0 / 255)  # light green
                cairo.rectangle(px, py, box_width, box_heigh)
                cairo.fill()

                cairo.set_source_rgb(204.0 / 255, 229.0 / 255, 204.0 / 255)  # green
                cairo.rectangle(px, py, box_width, title_heigh)
                cairo.fill()

                ## Title
                cairo.select_font_face("Georgia");
                cairo.set_source_rgb(59.0 / 255, 143.0 / 255, 0.0 / 255)  # dark green
                # cairo.set_source_rgb(0.0 / 255, 0.0 / 255, 0.0 / 255)  # green
                cairo.move_to(px + 5, py + 25)
                cairo.set_font_size(17)
                cairo.show_text(vname)

                for i in range(len(states)):
                    ## States
                    ny = py + title_heigh + (i + 1) * delta_state
                    cairo.set_source_rgb(204.0 / 255, 229.0 / 255, 204.0 / 255)  # green
                    cairo.move_to(px, ny)
                    cairo.line_to(px + box_width, ny)
                    cairo.stroke()

                    # Text for states
                    cairo.select_font_face("Georgia")
                    cairo.set_source_rgb(69.0 / 255, 163.0 / 255, 0.0 / 255)  # dark green
                    cairo.set_font_size(14)
                    cairo.move_to(px + 5, ny - 10)
                    cairo.show_text(states[i])

        return False

    def on_mode(self, radio_tool):
        if not radio_tool.get_active():
            return True

        if radio_tool.get_label() == "bedit":
            self.mode = Mode.edit
        if radio_tool.get_label() == "brun":
            self.mode = Mode.run
            #TODO edit buttons must be invisible
        print self.mode

    def on_edit_mode(self, radioTool):
        if not radioTool.get_active():
            return True
        # Radio selected
        if radioTool.get_label() == "bvertex":
            self.mode_edit = ModeEdit.vertex
            print "node mode", radioTool.get_active(), self.mode_edit, radioTool.get_label()
        elif radioTool.get_label() == "bedge":
            self.mode_edit = ModeEdit.edge
        elif radioTool.get_label() == "bmanual":
            self.mode_edit = ModeEdit.manual
        elif radioTool.get_label() == "bdelete":
            self.mode_edit = ModeEdit.delete
        else:
            print "not supported"

    def motion_event(self, *arg):
        # print "momving mouse", arg
        pass

    def onDeleteWindow(self, *args):
        Gtk.main_quit(*args)

    def onButtonPressed(self, button):
        print("Hello World!")

