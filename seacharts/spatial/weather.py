from seacharts.layers import Layer
from .spatial import SpatialData


class WeatherData(SpatialData):
    def __post_init__(self):
        ...

    @property
    def layers(self) -> list[Layer]:
        return []

    @property
    def loaded(self) -> bool:
        return any(self.layers)
