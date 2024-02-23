"""
Contains the Environment class for collecting and manipulating loaded spatial data.
"""
from seacharts.core import Scope, MapFormat, DataParser, S57Parser, FGDBParser
from .map import MapData
from .user import UserData
from .weather import WeatherData

class Environment:
    def __init__(self, settings: dict):
        self.scope = Scope(settings)
        self.parser = None
        self.set_parser()
        self.map = MapData(self.scope)
        self.user = UserData(self.scope)
        self.weather = WeatherData(self.scope)
        self.map.load_existing_shapefiles()
        if not self.map.loaded:
            self.map.parse_resources_into_shapefiles()

    def set_parser(self):
        if self.scope.type is MapFormat.S57:
            self.parser = S57Parser(self.scope.extent.bbox, self.scope.resources)
        elif self.scope.type is MapFormat.FGDB:
            self.parser = FGDBParser(self.scope.extent.bbox, self.scope.resources)
