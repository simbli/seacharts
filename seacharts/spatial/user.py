from seacharts.layers import Layer
from .spatial import SpatialData


class UserData(SpatialData):
    def __post_init__(self):
        self.shapes = {}

    @property
    def layers(self) -> list[Layer]:
        return list(self.shapes.values())
