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
        # return self.name

    def records_as_geometry(self, records: list[dict]) -> None:
        geometries = []

        if len(records) > 0:
            for record in records:
                geom_tmp = self._record_to_geometry(record)
                if isinstance(geom_tmp, geo.Polygon):
                    geometries.append(geom_tmp)
            self.geometry = self.as_multi(geometries)

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


@dataclass
class WeatherLayer:
    time: int
    data: list[list[float]]


@dataclass
class VirtualWeatherLayer:
    name: str
    weather: list[WeatherLayer]
