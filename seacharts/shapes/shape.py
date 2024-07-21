"""
Contains the Shape base class for creating and manipulating shapes.
"""
from abc import ABC
from dataclasses import dataclass
from typing import Any
from shapely import geometry as geo, ops


@dataclass
class Shape(ABC):
    geometry: geo.base.BaseGeometry = None
    color: str = None
    z_order: int = None
    artist: Any = None
    # name: str = None

    def simplify(self, tolerance: int, preserve_topology: bool = True) -> None:
        self.geometry = self.geometry.simplify(tolerance, preserve_topology)

    def clip(self, bbox: tuple[int, int, int, int]) -> None:
        bounding_box = geo.box(*bbox)
        self.geometry = bounding_box.intersection(self.geometry)

    def buffer(self, distance: int) -> None:
        self.geometry = self.geometry.buffer(distance)

    def merge(self, other: "Shape") -> None:
        self.geometry = self.geometry.union(other.geometry)

    def closest_points(self, geometry: Any) -> geo.Point:
        return ops.nearest_points(self.geometry, geometry)[1]

    @property
    def name(self) -> str:
        return self.__class__.__name__
    @property
    def mapping(self) -> dict:
        return geo.mapping(self.geometry)

    @staticmethod
    def _record_to_geometry(record: dict) -> Any:
        return geo.shape(record["geometry"])

    @staticmethod
    def as_multi(geometry) -> Any:
        if isinstance(geometry[0], geo.Point):
            return geo.MultiPoint(geometry)
        elif isinstance(geometry[0], geo.Polygon):
            return geo.MultiPolygon(geometry)
        elif isinstance(geometry[0], geo.LineString):
            return geo.MultiLineString(geometry)
        elif isinstance(geometry[0], geo.MultiPolygon):
            return geometry[0]
        else:
            raise NotImplementedError(type(geometry))

    @staticmethod
    def collect(geometries: list[Any]) -> Any:
        if any(not g.is_valid for g in geometries):
            geometries = [g.buffer(0) if not g.is_valid else g for g in geometries]
        geometry = ops.unary_union(geometries)
        if not geometry.is_valid:
            geometry = geometry.buffer(0)
        return geometry
