from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

import seacharts.data.config as config


@dataclass
class Extent:
    size: Tuple[int, int] = None
    origin: Tuple[int, int] = None
    center: Tuple[int, int] = None
    bbox: Tuple[int, int, int, int] = field(init=False)
    area: int = field(init=False)

    def __post_init__(self):
        if self.origin is not None and self.center is not None:
            raise ValueError(
                f"Multiple location arguments given."
            )
        defaults = config.read_settings()

        if self.origin is None:
            key = 'center'
            if self.center is None:
                default = config.parse(key, defaults)
                self.center = int(default[0]), int(default[1])
            config.validate(key, self.center, tuple, int, 2)
        else:
            config.validate('center', self.origin, tuple, int, 2)

        key = 'size'
        if self.size is None:
            default = config.parse(key, defaults)
            self.size = int(default[0]), int(default[1])
        config.validate(key, self.size, tuple, int, 2)

        if self.center is None:
            self._center_from_origin()
        else:
            self._origin_from_center()

        self.bbox = self._bounding_box_from_origin_size()

        if self.size[0] < 1 or self.size[1] < 1:
            raise ValueError(
                f"Input size (width / x_max, height / y_max) "
                f"must be strictly positive."
            )
        self.area = self.size[0] * self.size[1]

    def _origin_from_center(self):
        self.origin = (self.center[0] - self.size[0] // 2,
                       self.center[1] - self.size[1] // 2)

    def _center_from_origin(self):
        self.center = (self.origin[0] + self.size[0] // 2,
                       self.origin[1] + self.size[1] // 2)

    def _bounding_box_from_origin_size(self):
        x_min, y_min = self.origin
        x_max, y_max = x_min + self.size[0], y_min + self.size[1]
        return x_min, y_min, x_max, y_max
