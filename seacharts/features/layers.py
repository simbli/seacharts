from abc import ABC, abstractmethod

from .details import Rocks, Shallows
from .ocean import Seabed
from .surface import Land, Shore


class Layer(ABC):
    def __init__(self, shapefile):
        self._shapes = {f.__name__: shapefile(f) for f in self.features}

    def __getitem__(self, item):
        return self._shapes[item.capitalize()]

    def __getattr__(self, item):
        return self.__getitem__(item)

    @property
    @abstractmethod
    def features(self):
        raise NotImplementedError


class Ocean(Layer):
    features = (Seabed,)


class Surface(Layer):
    features = (Land, Shore)


class Details(Layer):
    features = (Rocks, Shallows)
