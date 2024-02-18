"""
Contains the Environment class for collecting and manipulating loaded spatial data.
"""
from seacharts.core import Scope
from .map import MapData
from .user import UserData
from .weather import WeatherData


class Environment:
    def __init__(self, settings: dict):
        self.scope = Scope(settings)
        self.map = MapData(self.scope)
        self.user = UserData(self.scope)
        self.weather = WeatherData(self.scope)

        self.map.load_existing_shapefiles()
        if not self.map.loaded:
            self.map.parse_resources_into_shapefiles()
