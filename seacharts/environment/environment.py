from dataclasses import dataclass
from numbers import Number
from typing import Container, Generator

from .feature import Seabed, Land, Shore, Shallows, Rocks


@dataclass
class Environment(Container):
    seabed: Seabed = None
    land: Land = None
    shore: Shore = None
    shallows: Shallows = None
    rocks: Rocks = None

    def __iter__(self) -> Generator:
        for key in self.__dict__:
            attribute = getattr(self, key)
            if attribute is not None:
                yield attribute

    def __contains__(self, item) -> bool:
        return getattr(self, item) is not None

    @property
    def _all_features(self) -> list:
        return [getattr(self, key) for key in self.__dict__ if key in self]

    def obstacles(self, min_depth: Number, buffer: Number = 0) -> tuple:
        shapes = []
        for feature in self._all_features:
            for shape in feature:
                if shape.depth <= min_depth:
                    shapes.append(shape)
        if not shapes:
            return ()
        else:
            return tuple(shapes[0].convex_union(shapes, buffer))
