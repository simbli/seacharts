from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import Any

from shapely import geometry as geo
from shapely import ops

from seacharts.parser import ShapefileParser


@dataclass
class Drawable:
    scale: float = field(init=False, repr=False)
    color: str = field(init=False, repr=False)
    z_order: int = field(init=False, repr=False)
    artist: Any = field(init=False, repr=False)


@dataclass
class Coordinates:
    x: float
    y: float


@dataclass
class Vector(Coordinates):
    pass


@dataclass
class Radial:
    radius: float


@dataclass
class Oriented:
    heading: float
    in_degrees: bool = True


@dataclass
class ZeroDepth:
    depth = 0


@dataclass
class SingleDepth:
    depth: int


@dataclass
class MultiDepth:
    @property
    def depth(self) -> None:
        raise AttributeError("Multi-depth shapes have no single depth.")


@dataclass
class Shape(Drawable, ABC):
    geometry: geo.base.BaseGeometry = None

    def simplify(self, tolerance: int, preserve_topology: bool = True) -> None:
        self.geometry = self.geometry.simplify(tolerance, preserve_topology)

    def clip(self, bbox: tuple[int, int, int, int]) -> None:
        bounding_box = geo.box(*bbox)
        self.geometry = bounding_box.intersection(self.geometry)

    def buffer(self, distance: int) -> None:
        self.geometry = self.geometry.buffer(distance)

    def merge(self, other: Shape) -> None:
        self.geometry = self.geometry.union(other.geometry)

    def closest_points(self, geometry: Any) -> geo.Point:
        return ops.nearest_points(self.geometry, geometry)[1]

    @property
    def mapping(self) -> dict:
        return geo.mapping(self.geometry)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @staticmethod
    def _record_to_geometry(record: dict) -> Any:
        return geo.shape(record["geometry"])

    @staticmethod
    def as_multi(geometry: Any) -> Any:
        if isinstance(geometry, geo.Point):
            return geo.MultiPoint([geometry])
        elif isinstance(geometry, geo.Polygon):
            return geo.MultiPolygon([geometry])
        elif isinstance(geometry, geo.LineString):
            return geo.MultiLineString([geometry])
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


@dataclass
class Layer(Shape, ABC):
    @property
    def _external_labels(self) -> list[str]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def label(self) -> str:
        return self.name.lower()

    def save(self, parser: ShapefileParser) -> None:
        parser.write(self)

    def load_shapefile(self, parser: ShapefileParser) -> None:
        records = list(parser.read_shapefile(self.label))
        if len(records) > 0:
            self.geometry = self._record_to_geometry(records[0])
            if isinstance(self.geometry, geo.Polygon):
                self.geometry = self.as_multi(self.geometry)

    def load_fgdb(self, parser: ShapefileParser) -> list[dict]:
        depth = self.depth if hasattr(self, "depth") else 0
        return list(parser.read_fgdb(self.label, self._external_labels, depth))

    def unify(self, records: list[dict]) -> None:
        geometries = [self._record_to_geometry(r) for r in records]
        self.geometry = self.collect(geometries)


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
