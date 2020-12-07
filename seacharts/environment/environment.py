from dataclasses import dataclass
from typing import Container

from .feature import Seabed, Land, Shore, Shallows, Rocks


@dataclass
class Environment(Container):
    seabed: Seabed = None
    land: Land = None
    shore: Shore = None
    shallows: Shallows = None
    rocks: Rocks = None

    def __iter__(self):
        for key in self.__dict__:
            attribute = getattr(self, key)
            if attribute is not None:
                yield attribute

    def __getattr__(self, item):
        if item in self.__dict__:
            return getattr(self, item)
        else:
            raise AttributeError(
                f"{self.__class__.__qualname__} has no attribute {item}"
            )

    def __contains__(self, item):
        return self.__getattr__(item) is not None
