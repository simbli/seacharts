"""
Contains the Layer class and depth-specific types for layered spatial data.
"""
from abc import ABC
from dataclasses import dataclass, field

from shapely import geometry as geo

from seacharts.layers.types import ZeroDepth, SingleDepth, MultiDepth
from seacharts.shapes import Shape


@dataclass
class Layer(Shape, ABC):
    geometry: geo.MultiPolygon = field(default_factory=geo.MultiPolygon)
    depth: int = None

    @property
    def label(self) -> str:
        return self.name.lower()

    def records_as_geometry(self, records: list[dict]) -> None:
        if len(records) > 0:
            self.geometry = self._record_to_geometry(records[0])
            if isinstance(self.geometry, geo.Polygon):
                self.geometry = self.as_multi(self.geometry)

    def unify(self, records: list[dict]) -> None:
        geometries = [self._record_to_geometry(r) for r in records]
        self.geometry = self.collect(geometries)


@dataclass
class ZeroDepthLayer(Layer, ZeroDepth, ABC):
    ...


@dataclass
class SingleDepthLayer(Layer, SingleDepth, ABC):
    @property
    def name(self) -> str:
        return self.__class__.__name__ + f"{self.depth}m"


@dataclass
class MultiDepthLayer(Layer, MultiDepth, ABC):
    ...
