from dataclasses import dataclass


@dataclass
class Extent:
    def __init__(self, settings: dict):
        self.size = tuple(settings["enc"].get("size", (0, 0)))

        if "origin" in settings["enc"]:
            self.origin = tuple(settings["enc"].get("origin", (0, 0)))
            self.center = self._center_from_origin()

        if "center" in settings["enc"]:
            self.center = tuple(settings["enc"].get("center", (0, 0)))
            self.origin = self._origin_from_center()

        self.bbox = self._bounding_box_from_origin_size()
        self.area: int = self.size[0] * self.size[1]

    def _origin_from_center(self) -> tuple[int, int]:
        return (
            self.center[0] - self.size[0] / 2,
            self.center[1] - self.size[1] / 2,
        )

    def _center_from_origin(self) -> tuple[int, int]:
        return (
            self.origin[0] + self.size[0] / 2,
            self.origin[1] + self.size[1] / 2,
        )

    def _bounding_box_from_origin_size(self) -> tuple[int, int, int, int]:
        x_min, y_min = self.origin
        x_max, y_max = x_min + self.size[0], y_min + self.size[1]
        return x_min, y_min, x_max, y_max
