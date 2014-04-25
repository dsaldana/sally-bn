
from abc import ABCMeta, abstractmethod

class GraphicObject:

    selected = False
    translatable = False


    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def is_on_point(self, p):
        pass
