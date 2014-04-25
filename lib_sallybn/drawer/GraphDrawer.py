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
from gi.repository import Gtk, Gdk

from lib_sallybn.drawer import color
from lib_sallybn.drawer.GStateBox import box_width, title_height, delta_state, GStateBox


class GraphDrawer:
    def __init__(self):
        #### Objects to show #####
        self.objects_to_show = []
        self.selected_object = None

        # Transform for scale
        self._transform = None
        # Translations
        self._translation = [0, 0]
        self._last_translation = [0, 0]
        # Scale and zoom
        self._scale = 1
        self._delta_zoom = 0.1

        ##Viewer mode
        self.viewer_mode = True

        self.area = Gtk.DrawingArea()
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.SCROLL_MASK |
                             Gdk.EventMask.SMOOTH_SCROLL_MASK | Gdk.EventMask.ALL_EVENTS_MASK)

        self.area.connect("motion-notify-event", self.on_motion_event)
        self.area.connect("draw", self.on_drawing_area_draw)
        self.area.connect("scroll-event", self.on_scroll)
        self.area.connect("button-press-event", self.on_button_press)
        self.area.connect("button-release-event", self.on_button_release)

        #Mouse events
        self.button_pressed = False
        self.clicked_point = None
        self.area.set_visible(True)

        self.clicked_element_listener = None
        self.double_clicked_element_listener = None
        self.clicked_clear_space_listener = None
        self.right_click_elem_listener = None

    def get_drawing_area(self):
        return self.area

    def transform_point(self, p):
        """ Transform a point based on applied scale.
        """
        new_p = self._transform.transform_point(p[0], p[1])
        return new_p

    def on_button_press(self, widget, event):
        """
        Button pressed on drawing area.
        """
        self.button_pressed = True
        p = [event.x, event.y]
        self.clicked_point = p

        # Transformed point
        tp = self.transform_point(p)
        obj_in_point = None

        if self.clicked_element_listener is not None:
            for o in self.objects_to_show:
                if o.is_on_point(tp):
                    obj_in_point = o
                    break

        self.selected_object = obj_in_point

        # double click
        if obj_in_point is not None and \
                        event.button == 1 and \
                        event.type == Gdk.EventType._2BUTTON_PRESS:
            self.double_clicked_element_listener(obj_in_point)
            self.button_pressed = False

        ## Click on edit area to TRANSLATE
        elif event.button == 1:
            # # For translation in drawing area.
            self._last_translation[0] += self._translation[0]
            self._last_translation[1] += self._translation[1]


    def on_button_release(self, widget, event):
        """
        Button release on the drawing area.
        """
        self.button_pressed = False

        p = [event.x, event.y]

        dx, dy = [self.clicked_point[0] - p[0], self.clicked_point[1] - p[1]]
        click_distance = math.hypot(dx, dy)


        # normal click
        if click_distance < 10.0:
            self._translation = [0, 0]

            # Transformed point
            tp = self.transform_point(p)
            obj_in_point = None

            if self.clicked_element_listener is not None:
                for o in self.objects_to_show:
                    if o.is_on_point(tp):
                        obj_in_point = o
                        break

            #Non selected object
            if obj_in_point is None:
                if event.button == 1:
                    # Notify clear space
                    self.clicked_clear_space_listener(tp)

            # selected
            else:
                ## Right click on object
                if event.button == 3:
                    self.right_click_elem_listener(obj_in_point, event)

                # Notify clicked object
                elif event.button == 1:
                    self.clicked_element_listener(obj_in_point)

        self.clicked_point = None



    def on_motion_event(self, widget, event):
        """
        Event generated by the mouse motion on the drawing area.
        """
        p = self.transform_point([event.x, event.y])

        if self.clicked_point is None:
            return

        if not self.button_pressed:
            return

        # Move the object
        if  self.selected_object is not None:
            if self.selected_object.translatable and self.button_pressed:
                self.selected_object.x, self.selected_object.y = p
                self.repaint()

        # MOve the world
        else:
            # translate world  is not None  and
            if self.viewer_mode:
                p = [event.x, event.y]

                dx, dy = [self.clicked_point[0] - p[0], self.clicked_point[1] - p[1]]
                self._translation[0] = -dx / self._scale
                self._translation[1] = -dy / self._scale

                self.area.queue_draw()

    def on_scroll(self, widget, event):
        """
        Scroll event by the mouse. It modifies the scale for drawing.
        """
        self._scale -= self._delta_zoom * event.delta_y
        self.area.queue_draw()

    def on_drawing_area_draw(self, drawing_area, cairo):
        """
        Draw on the drawing area!
        """
        # Sacale
        cairo.scale(self._scale, self._scale)
        # Translate
        tx = self._translation[0] + self._last_translation[0]
        ty = self._translation[1] + self._last_translation[1]
        cairo.translate(tx, ty)

        print (tx, ty), self._last_translation

        # Get transformation
        self._transform = cairo.get_matrix()
        self._transform.invert()

        #### Drawing ####
        # Background
        cairo.set_source_rgb(*color.white)
        cairo.rectangle(-10000, -10000, 100000, 1000000)
        cairo.fill()

        #TODO dynamic arrow

        # show objects
        for o in self.objects_to_show:
            o.draw(cairo)

    def restore_zoom(self):
        self._translation = [0, 0]
        self._last_translation = [0, 0]
        self._scale = 1
        self.area.queue_draw()


    def point_in_state(self, p, vertex_locations, marginals):
        """
        :p point to evaluate [x,y]
        :param vertex_locations dic with name and point, ex. {"v1":[x,y]}
        :param marginals dic with marginal probabilities to all variables
            ex. {"v1":{"state1": 0.5, "state2": 0.5}}
        :return: ("vertex", "state")
        """
        x, y = p

        for v, v_position in vertex_locations.iteritems():
            # states of vertex
            v_states = marginals[v].keys()
            box_heigh = GStateBox.get_box_height(v_states)

            # go to left-upper corner
            x_corner = v_position[0] - box_width / 2.0
            y_corner = v_position[1] - box_heigh / 2.0

            #if point.x is not in range
            if not x_corner < x <= x_corner + box_width:
                continue

            # evaluate each state for p.y
            for i in range(len(v_states)):
                ny = y_corner + title_height + i * delta_state
                ny_next = y_corner + title_height + (i + 1) * delta_state

                if ny < y <= ny_next:
                    return v, v_states[i]
        return None



    ######## SET GRAPHICAL OBJECTS
    def set_graphic_objects(self, graphic_objects):
        """ set a dynamic arrow to show based on mouse motion.
        """
        self.objects_to_show = graphic_objects
        self.area.queue_draw()

    def set_viewer_mode(self, active):
        self.viewer_mode = active

    def repaint(self):
        self.area.queue_draw()

