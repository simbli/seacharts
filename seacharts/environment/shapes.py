import numpy as np
import shapely.geometry as geom
from shapely.affinity import rotate
from shapely.ops import cascaded_union


class Shape:
    def __init__(self, depth, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.depth = depth

    @property
    def mapping(self):
        return geom.mapping(self)


class Position(Shape, geom.Point):
    type = 'Point'

    def __init__(self, point, depth=0):
        super().__init__(depth, point)

    def line_to(self, target):
        return Line(self, target)

    def is_left_of(self, line):
        positions = line.start, line.end, self
        return geom.LinearRing((p.coordinates for p in positions)).is_ccw


class Line(Shape, geom.LineString):
    type = 'LineString'

    def __init__(self, start, end, depth=None):
        if not all(isinstance(p, Position) for p in (start, end)):
            raise TypeError(
                f"Line should contain exactly 2 {Position} objects"
            )
        self.start = start
        self.end = end
        self.vector = (end.x - start.x, end.y - start.y)
        super().__init__(depth, (start.coords[0], end.coords[0]))


class Area(Shape, geom.Polygon):
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

    def convex_union(self, polygons, margin=0):
        union = [self.cascaded(p.buffer(margin).convex_hull) for p in polygons]
        return [p.convex_hull for p in self.cascaded(union)]

    @staticmethod
    def cascaded(polygons):
        union = cascaded_union(polygons)
        if isinstance(union, geom.MultiPolygon):
            union = list(union)
        return union
