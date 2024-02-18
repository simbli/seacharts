"""
Contains convenience classes for creating and manipulating line-based shapes.
"""
from dataclasses import dataclass

from shapely import geometry as geo

from seacharts.shapes import shape


@dataclass
class Line(shape.Shape):
    points: list[tuple[float, float]] = None

    def __post_init__(self):
        if self.points is None or len(self.points) < 2:
            raise ValueError(
                f"{self.__class__.__name__} must contain at least "
                f"2 pairs of coordinates"
            )
        self.geometry = geo.LineString(self.points)


@dataclass
class Arrow(shape.Shape):
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
