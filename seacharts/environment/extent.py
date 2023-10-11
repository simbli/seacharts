from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Extent:
    def __init__(self, settings: dict):
        self.utm_zone: int = settings["enc"]["utm_zone"]
        self.size: Tuple[int, int] = settings["enc"]["size"]
        self.size = self.size[0], self.size[1]

        self.origin: Tuple[int, int] = settings["enc"]["origin"]
        self.origin = self.origin[0], self.origin[1]

        if "center" in settings["enc"]:
            self.center: Tuple[int, int] = settings["enc"]["center"]
            self.center = self.center[0], self.center[1]
            self._origin_from_center()
        else:
            self._center_from_origin()

        self.bbox: Tuple[int, int, int, int] = self._bounding_box_from_origin_size()
        self.area: int = self.size[0] * self.size[1]

    def _origin_from_center(self) -> None:
        self.origin = (self.center[0] - self.size[0] / 2.0, self.center[1] - self.size[1] / 2.0)

    def _center_from_origin(self) -> None:
        self.center = (self.origin[0] + self.size[0] / 2.0, self.origin[1] + self.size[1] / 2.0)

    def _bounding_box_from_origin_size(self) -> Tuple[int, int, int, int]:
        x_min, y_min = self.origin
        x_max, y_max = x_min + self.size[0], y_min + self.size[1]
        return x_min, y_min, x_max, y_max
