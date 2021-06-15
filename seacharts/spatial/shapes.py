from __future__ import annotations

from dataclasses import dataclass, InitVar

from shapely import affinity, geometry as geo

from . import base


@dataclass
class Area(base.Shape):
    geometry: geo.Polygon = geo.Polygon()


@dataclass
class Body(Area, base.Oriented, base.Coordinates):
    def __post_init__(self):
        self.center = geo.Point(self.x, self.y)
        self.geometry = self.rotate(self._body_polygon())

    def _body_polygon(self) -> geo.Polygon:
        raise NotImplementedError

    def rotate(self, polygon):
        return affinity.rotate(
            polygon, -self.heading, use_radians=not self.in_degrees,
            origin=(self.center.x, self.center.y)
        )


@dataclass
class Ship(Body):
    dimensions = 16, 80
    scale: float = 1.0
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

    @property
    def parameters(self):
        return (self.x, self.y, self.heading,
                self.scale, self.lon_scale, self.lat_scale)

    @property
    def head(self):
        return self.x, self.y + 200 * self.lon_scale

    @property
    def starboard_bow(self):
        return self.x + 100 * self.lat_scale, self.y + 80 * self.lon_scale

    @property
    def starboard_side(self):
        return self.x + 100 * self.lat_scale, self.y - 40 * self.lon_scale

    @property
    def starboard_aft(self):
        return self.x + 50 * self.lat_scale, self.y - 100 * self.lon_scale

    @property
    def port_aft(self):
        return self.x - 50 * self.lat_scale, self.y - 100 * self.lon_scale

    @property
    def port_side(self):
        return self.x - 100 * self.lat_scale, self.y - 40 * self.lon_scale

    @property
    def port_bow(self):
        return self.x - 100 * self.lat_scale, self.y + 80 * self.lon_scale

    @property
    def horizon(self) -> geo.Polygon:
        return self.rotate(geo.Polygon([
            self.head,
            self.starboard_bow,
            self.starboard_side,
            self.starboard_aft,
            self.port_aft,
            self.port_side,
            self.port_bow,
        ]))

    @property
    def starboard_bow_horizon(self) -> geo.Polygon:
        return self.rotate(geo.Polygon([
            self.center.coords[0],
            self.head,
            self.starboard_bow,
        ]))

    @property
    def starboard_side_horizon(self) -> geo.Polygon:
        return self.rotate(geo.Polygon([
            self.center.coords[0],
            self.starboard_bow,
            self.starboard_side,
        ]))

    @property
    def starboard_aft_horizon(self) -> geo.Polygon:
        return self.rotate(geo.Polygon([
            self.center.coords[0],
            self.starboard_side,
            self.starboard_aft,
        ]))

    @property
    def rear_aft_horizon(self) -> geo.Polygon:
        return self.rotate(geo.Polygon([
            self.center.coords[0],
            self.starboard_aft,
            self.port_aft,
        ]))

    @property
    def port_aft_horizon(self) -> geo.Polygon:
        return self.rotate(geo.Polygon([
            self.center.coords[0],
            self.port_aft,
            self.port_side,
        ]))

    @property
    def port_side_horizon(self) -> geo.Polygon:
        return self.rotate(geo.Polygon([
            self.center.coords[0],
            self.port_side,
            self.port_bow,
        ]))

    @property
    def port_bow_horizon(self) -> geo.Polygon:
        return self.rotate(geo.Polygon([
            self.center.coords[0],
            self.port_bow,
            self.head,
        ]))

    @property
    def horizon_sectors(self) -> dict:
        return dict(
            port_bow=self.port_bow_horizon,
            port_side=self.port_side_horizon,
            port_aft=self.port_aft_horizon,
            rear_aft=self.rear_aft_horizon,
            starboard_aft=self.starboard_aft_horizon,
            starboard_side=self.starboard_side_horizon,
            starboard_bow=self.starboard_bow_horizon,
        )


@dataclass
class Waypoint(Area, base.Radial, base.Coordinates):
    resolution: InitVar[int] = 0

    def __post_init__(self, resolution):
        self.center = geo.Point(self.x, self.y)
        self.geometry = self.center.buffer(self.radius, resolution=resolution)

    def contains(self, x, y):
        return self.geometry.contains(geo.Point(x, y))


class Path:
    def __init__(self, color, resolution=0):
        self.color = color
        self.resolution = resolution
        self.waypoints = []
        self.edges = []
        self.artist = None

    @property
    def multi_shape(self):
        return base.Shape.collect(
            [x.geometry for x in self.waypoints] + self.edges
        )

    def add_waypoint(self, x, y, index=None, edge=False):
        radius = 30
        if index is None:
            prev_wp = self.waypoints[-1] if self.waypoints else None
            waypoint = Waypoint(x, y, radius, resolution=self.resolution)
            if prev_wp:
                prev_wp.next = waypoint
                edge = self.edge_between(prev_wp, waypoint)
                self.edges.append(edge)
            self.waypoints.append(waypoint)
        else:
            if not edge:
                if index > 0:
                    prev_wp = self.waypoints[index - 1]
                else:
                    prev_wp = None
                if index < len(self.waypoints) - 1:
                    next_wp = self.waypoints[index + 1]
                else:
                    next_wp = None
                waypoint = Waypoint(x, y, radius, resolution=self.resolution)
                self.waypoints.pop(index)
                self.waypoints.insert(index, waypoint)
                if prev_wp:
                    edge1 = self.edge_between(prev_wp, waypoint)
                    self.edges.pop(index - 1)
                    self.edges.insert(index - 1, edge1)
                if next_wp:
                    edge2 = self.edge_between(waypoint, next_wp)
                    self.edges.pop(index)
                    self.edges.insert(index, edge2)
            else:
                prev_wp = self.waypoints[index]
                if index < len(self.waypoints) - 1:
                    next_wp = self.waypoints[index + 1]
                else:
                    next_wp = None
                waypoint = Waypoint(x, y, radius, resolution=self.resolution)
                self.waypoints.insert(index + 1, waypoint)
                new_edge = self.edge_between(prev_wp, waypoint)
                self.edges.insert(index, new_edge)
                if next_wp:
                    self.edges[index + 1] = self.edge_between(waypoint,
                                                              next_wp)

    def remove_waypoint(self, index):
        self.waypoints.pop(index)
        if index == 0:
            if self.edges:
                self.edges.pop(0)
        elif index < len(self.waypoints):
            self.edges.pop(index)
            previous_wp = self.waypoints[index - 1]
            next_wp = self.waypoints[index]
            self.edges[index - 1] = self.edge_between(previous_wp, next_wp)
        else:
            self.edges.pop(-1)

    def locate_waypoint(self, x, y):
        for i, waypoint in enumerate(self.waypoints):
            if waypoint.contains(x, y):
                return i
        else:
            return None

    def locate_edge(self, x, y):
        for i, edge in enumerate(self.edges):
            if edge.contains(base.geo.Point(x, y)):
                return i
        else:
            return None

    @staticmethod
    def edge_between(wp1, wp2):
        line = wp1.line_between(wp1.center, wp2.center)
        return line.buffer(7, cap_style=2, join_style=3)
