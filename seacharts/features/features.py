import math
from abc import ABC

import numpy as np

from seacharts.files import Shapefile
from .shapes import Area, Position


class Feature(ABC):
    def __init__(self, shapes=()):
        self.shapefile = Shapefile(self.label, self.shape.type)
        self._shapes = shapes

    def __getitem__(self, item):
        return self._shapes[item]

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def label(self):
        return self.name.lower()

    @property
    def shapely(self):
        return self._shapes

    @property
    def coords(self):
        if not self._shapes:
            raise AttributeError(f"Feature {self.name} has no shapes")
        elif len(self._shapes) > 1:
            raise AttributeError(f"Feature {self.name} has several shapes")
        else:
            return self._shapes[0].coords

    @property
    def xy(self):
        return np.array(self.coords)

    @property
    def shape(self):
        raise NotImplementedError

    @property
    def depth_label(self):
        raise NotImplementedError

    @property
    def layer_label(self):
        raise NotImplementedError

    def load(self, bbox, external=None):
        self._shapes = tuple(self.read_shapes(bbox, external))

    def read_shapes(self, bbox, external):
        paths = external.file_paths if external else [None]
        layer = self.layer_label if external else None
        for path in paths:
            records = self.shapefile.read(bbox, path, layer)
            for record in records:
                yield self.record_to_shape(record, external)

    def record_to_shape(self, record, external_label):
        label = self.depth_label if external_label else 'depth'
        depth = record['properties'][label] if label else 0
        coords = record['geometry']['coordinates']
        if self.shape.type == 'Polygon':
            coords = coords[0][0] if external_label else coords[0]
        return self.shape(coords, depth)

    def write_to_shapefile(self):
        self.shapefile.write(self._shapes)


class Seabed(Feature):
    shape = Area
    layer_label = 'dybdeareal'
    depth_label = 'minimumsdybde'


class Land(Feature):
    shape = Area
    layer_label = 'landareal'
    depth_label = None
    pass


class Shore(Feature):
    shape = Area
    layer_label = 'torrfall'
    depth_label = None
    pass


class Rocks(Feature):
    shape = Position
    layer_label = 'skjer'
    depth_label = None
    pass


class Shallows(Feature):
    shape = Position
    layer_label = 'grunne'
    depth_label = 'dybde'
    pass


class Ship(Feature):
    shape = Position
    layer_label = None
    depth_label = None
    default_scale = 1.0
    default_heading = 103.0
    default_center = (44100, 6957400)
    ship_dimensions = (13.6, 74.7)

    def __init__(self, center=None, heading=None, scale=None):
        if center is None:
            self.center = Position(self.default_center)
        elif isinstance(center, Position):
            self.center = center
        else:
            raise TypeError(
                f"Ship center should be a {Position} object"
            )
        if heading is None:
            self.heading = self.default_heading
        elif isinstance(heading, int) or isinstance(heading, float):
            self.heading = heading
        else:
            raise TypeError(
                f"Ship heading should be a number in degrees"
            )
        if scale is None:
            self.scale = self.default_scale
        elif isinstance(scale, int) or isinstance(scale, float):
            self.scale = scale
        else:
            raise TypeError(
                f"Ship scale should be a number"
            )
        self._shapes = self.create_hull()
        super().__init__(self._shapes)

    @property
    def coords(self):
        return self.center.coords[0]

    @property
    def hull(self):
        return self._shapes[0].coords

    def create_hull(self):
        x, y = self.center.coords[0]
        w, h = (i * self.scale for i in self.ship_dimensions)
        x_min, x_max = x - w / 2, x + w / 2
        y_min, y_max = y - h / 2, y + h / 2 - w
        left_aft, right_aft = (x_min, y_min), (x_max, y_min)
        left_bow, right_bow = (x_min, y_max), (x_max, y_max)
        points = [left_aft, left_bow, (x, y + h / 2), right_bow, right_aft]
        angle, origin = -self.heading, self.center.coords[0]
        return (Area(points).rotate(angle, origin),)

    def update_position(self, fps, ship_velocity=7, speedup=10):
        step = ship_velocity * speedup / fps
        x, y = self.center.coords[0]
        x += math.sin(self.heading * math.pi / 180) * step
        y += math.cos(self.heading * math.pi / 180) * step
        self.center = Position((x, y))
        self._shapes = self.create_hull()
