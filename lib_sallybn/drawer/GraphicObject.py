
from abc import ABCMeta, abstractmethod

class GraphicObject:
    def __init__(self):
        __metaclass__ = ABCMeta


    @abstractmethod
    def draw(self):
        pass

    @abstractmethod
    def is_on_point(self, p):
        pass