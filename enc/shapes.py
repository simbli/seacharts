from abc import ABC, abstractmethod

from shapely.geometry import Point, Polygon


class Shape(ABC):
    def __init__(self, geometry, depth):
        self.depth = 0 if depth is None else depth
        self._geometry = geometry

    @abstractmethod
    def coordinates(self):
        raise NotImplementedError

    @staticmethod
    def is_coordinate_tuple(point):
        return isinstance(point, tuple) and len(point) == 2


class Position(Shape):
    def __init__(self, point, depth=None):
        if not self.is_coordinate_tuple(point):
            raise PositionFormatError(
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


class Area(Shape):
    def __init__(self, points, depth=None):
        if not all(self.is_coordinate_tuple(p) for p in points):
            raise AreaFormatError(
                f"Area should be a sequence of (E, N) coordinate tuples"
            )
        super().__init__(Polygon(points), depth)

    @property
    def coordinates(self):
        return self._geometry.exterior.coords

    @property
    def size(self):
        return self._geometry.area


class PositionFormatError(TypeError):
    pass


class AreaFormatError(TypeError):
    pass
