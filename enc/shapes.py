from abc import ABC, abstractmethod
from math import sqrt

from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon


class Shape(ABC):
    def __init__(self, geometry, depth=None):
        self.depth = 0 if depth is None else depth
        self._geometry = geometry

    def __repr__(self):
        return f"{self.__class__.__name__}{self.coordinates}"

    @abstractmethod
    def coordinates(self):
        raise NotImplementedError

    @staticmethod
    def is_coordinate_tuple(point):
        return isinstance(point, tuple) and len(point) == 2


class Position(Shape):
    def __init__(self, point, depth=None):
        if not self.is_coordinate_tuple(point):
            raise TypeError(
                f"Position should be a tuple of the form "
                f"(easting, northing) in meters"
            )
        super().__init__(Point(point), depth)

    @property
    def coordinates(self):
        return self._geometry.coords[0]

    @property
    def x(self):
        return self.coordinates[0]

    @property
    def y(self):
        return self.coordinates[1]

    def line_to(self, target):
        return Line(self, target)

    def is_left_of(self, line):
        positions = line.start, line.end, self
        return LinearRing((p.coordinates for p in positions)).is_ccw


class Line(Shape):
    def __init__(self, start, end, depth=None):
        if not all(isinstance(p, Position) for p in (start, end)):
            raise TypeError(
                f"Line should contain exactly 2 {Position} objects"
            )
        self.start = start
        self.end = end
        self.vector = (end.x - start.x, end.y - start.y)
        self.length = sqrt(sum(i ** 2 for i in self.vector))
        geometry = LineString((start.coordinates, end.coordinates))
        super().__init__(geometry, depth)

    @property
    def coordinates(self):
        return tuple(self._geometry.coords)


class Area(Shape):
    def __init__(self, points, depth=None):
        if not all(self.is_coordinate_tuple(p) for p in points):
            raise TypeError(
                f"Area should be a sequence of (E, N) coordinate tuples"
            )
        super().__init__(Polygon(points), depth)

    @property
    def coordinates(self):
        return tuple(self._geometry.exterior.coords)

    @property
    def size(self):
        return self._geometry.area


class Ship(Shape):
    ship_dimensions = (13.6, 74.7)

    def __init__(self, center, heading=0.0, scale=1.0):
        if isinstance(center, Position):
            self.center = center
        else:
            raise TypeError(
                f"Ship center should be a {Position} object"
            )
        if isinstance(heading, int) or isinstance(heading, float):
            self.heading = heading
        else:
            raise TypeError(
                f"Ship heading should be a number in degrees"
            )
        x, y = center.coordinates
        w, h = (i * scale for i in self.ship_dimensions)
        x_min, x_max = x - w / 2, x + w / 2
        y_min, y_max = y - h / 2, y + h / 2 - w
        left_aft, right_aft = (x_min, y_min), (x_max, y_min)
        left_bow, right_bow = (x_min, y_max), (x_max, y_max)
        points = (left_aft, left_bow, (x, y + h / 2), right_aft, right_bow)
        angle, origin = -self.heading, self.center.coordinates
        geometry = rotate(Polygon(points), angle=angle, origin=origin)
        super().__init__(geometry)

    @property
    def coordinates(self):
        return self.center.coordinates
