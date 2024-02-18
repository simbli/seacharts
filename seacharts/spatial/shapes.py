from dataclasses import dataclass, field

from shapely import affinity
from shapely import geometry as geo

from . import base


@dataclass
class Area(base.Shape):
    geometry: geo.Polygon = field(default_factory=geo.Polygon)

    @staticmethod
    def new_polygon(exterior: list, interiors=None) -> geo.Polygon:
        return geo.Polygon(exterior, interiors)


@dataclass
class Line(base.Shape):
    points: list[tuple[float, float]] = None

    def __post_init__(self):
        if self.points is None or len(self.points) < 2:
            raise ValueError(
                f"{self.__class__.__name__} must contain at least "
                f"2 pairs of coordinates"
            )
        self.geometry = geo.LineString(self.points)


@dataclass
class Arrow(base.Shape):
    start: tuple[float, float] = None
    end: tuple[float, float] = None
    width: float = None

    def __post_init__(self):
        if self.start is None or self.end is None:
            raise ValueError(
                f"{self.__class__.__name__} must have a start and an end point"
            )
        self.geometry = geo.LineString((self.start, self.end))

    @property
    def vector(self) -> tuple[float, float]:
        return self.end[0] - self.start[0], self.end[1] - self.start[1]

    def body(self, head_size: int) -> geo.Polygon:
        if not head_size >= 0:
            raise ValueError(
                f"{self.__class__.__name__} should have non-negative head size"
            )
        length = self.geometry.length
        arrow_head_length = max(length - head_size, 0)
        x1, y1 = self.start
        x2, y2 = self.geometry.interpolate(arrow_head_length).coords[0]
        unit = self.vector[0] / length, self.vector[1] / length
        dx1, dy1 = -unit[1] * self.width, unit[0] * self.width
        dx2, dy2 = dx1 * 3, dy1 * 3
        tip_left, tip_right = (x2 + dx2, y2 + dy2), (x2 - dx2, y2 - dy2)
        base_left, base_right = (x2 + dx1, y2 + dy1), (x2 - dx1, y2 - dy1)
        start_left, start_right = (x1 + dx1, y1 + dy1), (x1 - dx1, y1 - dy1)
        return geo.Polygon(
            (
                self.end,
                tip_left,
                base_left,
                start_left,
                start_right,
                base_right,
                tip_right,
            )
        )


@dataclass
class Circle(Area, base.Radial, base.Coordinates):
    def __post_init__(self):
        if self.radius <= 0:
            raise ValueError(
                f"{self.__class__.__name__} " f"should have a positive area"
            )
        self.center = geo.Point(self.x, self.y)
        self.geometry = geo.Polygon(self.center.buffer(self.radius))


@dataclass
class Body(Area, base.Oriented, base.Coordinates):
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
