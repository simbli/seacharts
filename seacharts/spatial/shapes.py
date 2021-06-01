from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from shapely import affinity, geometry as geo

from . import base


@dataclass
class Area(base.Shape):
    geometry: geo.Polygon = geo.Polygon()


@dataclass
class Body(Area, base.Oriented, base.Coordinates):
    def __post_init__(self):
        self.center = geo.Point(self.x, self.y)
        if self.in_degrees:
            angle = self.heading
        else:
            angle = self.heading * 180 / np.pi
        polygon = self._construct_body_shape()
        self.geometry = affinity.rotate(
            polygon, -angle, origin=(self.center.x, self.center.y)
        )

    def _construct_body_shape(self) -> geo.Polygon:
        raise NotImplementedError


@dataclass
class Ship(Body):
    ship_dimensions = 16, 80

    def _construct_body_shape(self) -> geo.Polygon:
        scale = 1.0
        x, y = self.x, self.y
        w, h = (d * scale for d in self.ship_dimensions)
        x_min, x_max = x - w / 2, x + w / 2
        y_min, y_max = y - h / 2, y + h / 2 - w
        left_aft, right_aft = (x_min, y_min), (x_max, y_min)
        left_bow, right_bow = (x_min, y_max), (x_max, y_max)
        coords = [left_aft, left_bow, (x, y + h / 2), right_bow, right_aft]
        return geo.Polygon(coords)
