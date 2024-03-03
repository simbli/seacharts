"""
Contains the Environment class for collecting and manipulating loaded spatial data.
"""
from seacharts.core import Scope, MapFormat, S57Parser, FGDBParser, DataParser
from .map import MapData
from .user import UserData
from .weather import WeatherData


class Environment:
    def __init__(self, settings: dict):
        self.scope = Scope(settings)
        self.parser = self.set_parser()
        self.map = MapData(self.scope, self.parser)
        self.map.parse_resources_into_shapefiles()
        self.user = UserData(self.scope, self.parser)
        self.weather = WeatherData(self.scope, self.parser)
        self.map.load_existing_shapefiles()
        if not self.map.loaded:
            self.map.parse_resources_into_shapefiles()

    def set_parser(self) -> DataParser:
        if self.scope.type is MapFormat.S57:
            return S57Parser(self.scope.extent.bbox, self.scope.resources, self.scope.autosize)
        elif self.scope.type is MapFormat.FGDB:
            return FGDBParser(self.scope.extent.bbox, self.scope.resources, self.scope.autosize)
