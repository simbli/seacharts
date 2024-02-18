from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field

from shapely import geometry as geo

from seacharts.layers.layer import Layer, ZeroDepth, SingleDepth, MultiDepth


@dataclass
class Regions(Layer, ABC):
    geometry: geo.MultiPolygon = field(default_factory=geo.MultiPolygon)


@dataclass
class ZeroDepthRegions(Regions, ZeroDepth, ABC):
    pass


@dataclass
class SingleDepthRegions(Regions, SingleDepth, ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__ + f"{self.depth}m"


@dataclass
class MultiDepthRegions(Regions, MultiDepth, ABC):
    pass


@dataclass
class Seabed(SingleDepthRegions):
    color = "seabed"
    z_order = -300
    _external_labels = [
        dict(layer="dybdeareal", depth="minimumsdybde"),
        dict(layer="grunne", depth="dybde"),
    ]


@dataclass
class Land(ZeroDepthRegions):
    color = "land"
    z_order = -100
    _external_labels = ["landareal"]


@dataclass
class Shore(ZeroDepthRegions):
    color = "shore"
    z_order = -200
    _external_labels = ["skjer", "torrfall", "landareal", "ikkekartlagtsjomaltomr"]
