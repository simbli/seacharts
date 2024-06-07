"""
Contains the WeatherData class for containing parsed weather data.
"""
from seacharts.layers import Layer
from .collection import DataCollection


class WeatherData(DataCollection):
    def __post_init__(self):
        ...
    @property
    def layers(self) -> list[Layer]:
        return []

    @property
    def loaded(self) -> bool:
        return any(self.layers)
