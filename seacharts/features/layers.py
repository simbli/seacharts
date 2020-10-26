from abc import ABC, abstractmethod

from .details import Rocks, Shallows
from .ocean import Seabed
from .surface import Land, Shore


class Layer(ABC):
    @property
    @abstractmethod
    def features(self):
        raise NotImplementedError


class Ocean(Layer):
    features = (Seabed,)

    def __init__(self, shapefile):
        self.seabed = shapefile(Seabed)


class Surface(Layer):
    features = (Land, Shore)

    def __init__(self, shapefile):
        self.land = shapefile(Land)
        self.shore = shapefile(Shore)


class Details(Layer):
    features = (Rocks, Shallows)

    def __init__(self, shapefile):
        self.rocks = shapefile(Rocks)
        self.shallows = shapefile(Shallows)
