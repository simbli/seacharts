import numpy as np
from shapely.affinity import rotate
from shapely.geometry import LinearRing, LineString, Point, Polygon, mapping


class Shape:
    def __init__(self, depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.depth = depth

    @property
    def mapping(self):
        return mapping(self)


class Position(Shape, Point):
    type = 'Point'

    def __init__(self, point, depth=0):
        super().__init__(depth, point)

    def line_to(self, target):
        return Line(self, target)

    def is_left_of(self, line):
        positions = line.start, line.end, self
        return LinearRing((p.coordinates for p in positions)).is_ccw


class Line(Shape, LineString):
    type = 'LineString'

    def __init__(self, start, end, depth=None):
        if not all(isinstance(p, Position) for p in (start, end)):
            raise TypeError(
                f"Line should contain exactly 2 {Position} objects"
            )
        self.start = start
        self.end = end
        self.vector = (end.x - start.x, end.y - start.y)
        super().__init__((start, end), depth)


class Area(Shape, Polygon):
    type = 'Polygon'

    def __init__(self, coords, depth=0):
        super().__init__(depth, shell=coords)

    @property
    def coords(self):
        return self.exterior.coords

    @property
    def xy(self):
        return np.array(self.exterior.coords)

    @property
    def __array_interface__(self):
        raise NotImplementedError

    def _get_coords(self):
        raise NotImplementedError

    def _set_coords(self, ob):
        raise NotImplementedError

    def rotate(self, angle, origin):
        return rotate(self, angle, origin)
