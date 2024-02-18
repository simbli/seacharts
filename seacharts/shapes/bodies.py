"""
Contains convenience classes for creating and manipulating spatial bodies.
"""
from dataclasses import dataclass

from shapely import geometry as geo, affinity

from . import areas, types


@dataclass
class Body(areas.Area, types.Oriented, types.Coordinates):
    scale: float = 1.0

    def __post_init__(self):
        self.center = geo.Point(self.x, self.y)
        self.geometry = self.rotate(self._body_polygon())

    def _body_polygon(self) -> geo.Polygon:
        raise NotImplementedError

    def rotate(self, polygon: geo.Polygon) -> geo.Polygon:
        return affinity.rotate(
            polygon,
            -self.heading,
            use_radians=not self.in_degrees,
            origin=(self.center.x, self.center.y),
        )


@dataclass
class Rectangle(Body):
    width: float = 0.0
    height: float = 0.0

    def _body_polygon(self) -> geo.Polygon:
        if not self.width > 0 or not self.height > 0:
            raise ValueError(
                f"{self.__class__.__name__} " f"should have a positive area"
            )
        return geo.Polygon(
            (
                (self.x - self.width, self.y - self.height),
                (self.x + self.width, self.y - self.height),
                (self.x + self.width, self.y + self.height),
                (self.x - self.width, self.y + self.height),
            )
        )


@dataclass
class Ship(Body):
    dimensions = 16, 80
    lon_scale: float = 10.0
    lat_scale: float = 10.0

    def _body_polygon(self) -> geo.Polygon:
        x, y = self.x, self.y
        w, h = (d * self.scale for d in self.dimensions)
        x_min, x_max = x - w / 2, x + w / 2
        y_min, y_max = y - h / 2, y + h / 2 - w
        left_aft, right_aft = (x_min, y_min), (x_max, y_min)
        left_bow, right_bow = (x_min, y_max), (x_max, y_max)
        coords = [left_aft, left_bow, (x, y + h / 2), right_bow, right_aft]
        return geo.Polygon(coords)
