from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from shapely import geometry as geo

from seacharts.layers.layer import Layer, ZeroDepth, SingleDepth, MultiDepth


@dataclass
class Locations(Layer, ABC):
    geometry: geo.MultiPoint = field(default_factory=geo.MultiPoint)


@dataclass
class ZeroDepthLocations(Locations, ZeroDepth, ABC):
    pass


@dataclass
class SingleDepthLocations(Locations, SingleDepth, ABC):
    pass


@dataclass
class MultiDepthLocations(Locations, MultiDepth, ABC):
    pass
