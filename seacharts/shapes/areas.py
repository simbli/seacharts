"""
Contains convenience classes for creating and manipulating area-based shapes.
"""
from dataclasses import dataclass, field

from shapely import geometry as geo

from . import shape, types


@dataclass
class Area(shape.Shape):
    geometry: geo.Polygon = field(default_factory=geo.Polygon)

    @staticmethod
    def new_polygon(exterior: list, interiors=None) -> geo.Polygon:
        return geo.Polygon(exterior, interiors)


@dataclass
class Circle(Area, types.Radial, types.Coordinates):
    def __post_init__(self):
        if self.radius <= 0:
            raise ValueError(
                f"{self.__class__.__name__} " f"should have a positive area"
            )
        self.center = geo.Point(self.x, self.y)
        self.geometry = geo.Polygon(self.center.buffer(self.radius))
