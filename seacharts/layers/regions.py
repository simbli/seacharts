"""
Contains the Regions class and depth-specific types for regional spatial data.
"""
from abc import ABC
from dataclasses import dataclass, field

from shapely import geometry as geo

from seacharts.layers.layer import Layer
from seacharts.layers.types import ZeroDepth, SingleDepth, MultiDepth


@dataclass
class Regions(Layer, ABC):
    geometry: geo.MultiPolygon = field(default_factory=geo.MultiPolygon)
    depth: int = None


@dataclass
class ZeroDepthRegions(Regions, ZeroDepth, ABC):
    ...


@dataclass
class SingleDepthRegions(Regions, SingleDepth, ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__ + f"{self.depth}m"


@dataclass
class MultiDepthRegions(Regions, MultiDepth, ABC):
    ...


@dataclass
class Seabed(SingleDepthRegions):
    ...


@dataclass
class Land(ZeroDepthRegions):
    ...


@dataclass
class Shore(ZeroDepthRegions):
    ...
