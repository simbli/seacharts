from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from typing import List, Any

from shapely import geometry as geo, ops


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
    def depth(self):
        raise AttributeError(
            f"Multi-depth shapes have no single depth."
        )


@dataclass
class Shape(Drawable, ABC):
    geometry: geo.base.BaseGeometry = None

    def simplify(self, tolerance, preserve_topology=True):
        self.geometry = self.geometry.simplify(tolerance, preserve_topology)

    def clip(self, bbox):
        bounding_box = geo.box(*bbox)
        self.geometry = bounding_box.intersection(self.geometry)

    def dilate(self, distance):
        self.geometry = self.geometry.buffer(
            distance, cap_style=2, join_style=3
        )

    def erode(self, distance):
        self.dilate(-distance)

    def merge(self, other: Shape):
        self.geometry = self.geometry.union(other.geometry)

    def closest_points(self, geometry):
        return ops.nearest_points(self.geometry, geometry)[1]

    @property
    def mapping(self) -> dict:
        return geo.mapping(self.geometry)

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def invalid(self):
        return not self.geometry.is_valid

    @staticmethod
    def is_multi(geometry):
        return (isinstance(geometry, geo.MultiPolygon)
                or isinstance(geometry, geo.GeometryCollection))

    @staticmethod
    def _record_to_geometry(record):
        return geo.shape(record['geometry'])

    @staticmethod
    def as_multi(geometry):
        if isinstance(geometry, geo.Point):
            return geo.MultiPoint([geometry])
        elif isinstance(geometry, geo.Polygon):
            return geo.MultiPolygon([geometry])
        elif isinstance(geometry, geo.LineString):
            return geo.MultiLineString([geometry])
        else:
            raise NotImplementedError(type(geometry))

    @staticmethod
    def collect(geometries):
        return ops.unary_union(geometries)

    @staticmethod
    def line_between(point1, point2):
        return geo.LineString([point1, point2])

    @staticmethod
    def arrow_head(points):
        return geo.Polygon(points)


@dataclass
class Layer(Shape, ABC):
    @property
    def _external_labels(self) -> List[str]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def label(self) -> str:
        return self.name.lower()

    def save(self, parser):
        parser.write(self)

    def load_shapefile(self, parser):
        records = list(parser.read_shapefile(self.label))
        if len(records) > 0:
            self.geometry = self._record_to_geometry(records[0])
            if isinstance(self.geometry, geo.Polygon):
                self.geometry = self.as_multi(self.geometry)

    def load_fgdb(self, parser):
        depth = self.depth if hasattr(self, 'depth') else 0
        return list(parser.read_fgdb(self.label, self._external_labels, depth))

    def unify(self, records):
        geometries = [self._record_to_geometry(r) for r in records]
        self.geometry = self.collect(geometries)


@dataclass
class Locations(Layer, ABC):
    geometry: geo.MultiPoint = geo.MultiPoint()


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
    geometry: geo.MultiPolygon = geo.MultiPolygon()


@dataclass
class ZeroDepthRegions(Regions, ZeroDepth, ABC):
    pass


@dataclass
class SingleDepthRegions(Regions, SingleDepth, ABC):
    @property
    def name(self):
        return self.__class__.__name__ + f"{self.depth}m"


@dataclass
class MultiDepthRegions(Regions, MultiDepth, ABC):
    pass
