"""
Contains the Layer class and depth-specific types for layered spatial data.
"""
from abc import ABC
from dataclasses import dataclass, field

from shapely import geometry as geo
from shapely.geometry import base as geobase
from shapely.ops import unary_union

from seacharts.layers.types import ZeroDepth, SingleDepth, MultiDepth
from seacharts.shapes import Shape


@dataclass
class Layer(Shape, ABC):
    geometry: geobase.BaseMultipartGeometry = field(default_factory=geo.MultiPolygon)
    depth: int = None

    @property
    def label(self) -> str:
        return self.name.lower()

    def _geometries_to_multi(self, multi_geoms, geometries, geo_class):
        if len(geometries):
            geometries = self.as_multi(geometries)
            multi_geoms.append(geometries)
        geom = unary_union(multi_geoms)
        if not isinstance(geom, geo_class):
            geom = geo_class([geom])
        return geom

    def records_as_geometry(self, records: list[dict]) -> None:
        geometries = []
        multi_geoms = []
        linestrings = []
        multi_linestrings = []
        if len(records) > 0:
            for record in records:
                geom_tmp = self._record_to_geometry(record)

                if isinstance(geom_tmp, geo.Polygon):
                    geometries.append(geom_tmp)
                elif isinstance(geom_tmp, geo.MultiPolygon):
                    multi_geoms.append(geom_tmp)
                elif isinstance(geom_tmp, geo.LineString):
                    linestrings.append(geom_tmp)
                elif isinstance(geom_tmp, geo. MultiLineString):
                    multi_linestrings.append(geom_tmp)

            if len(geometries) + len(multi_geoms) > 0:
                self.geometry = self._geometries_to_multi(multi_geoms, geometries, geo.MultiPolygon)

            elif len(linestrings) + len(multi_linestrings) > 0:
                self.geometry = self._geometries_to_multi(multi_linestrings, linestrings, geo.MultiLineString)

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
