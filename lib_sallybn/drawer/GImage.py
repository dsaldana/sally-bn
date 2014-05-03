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