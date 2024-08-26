"""
Contains the Environment class for collecting and manipulating loaded spatial data.
"""
from seacharts.core import Scope, MapFormat, S57Parser, FGDBParser, DataParser
from .map import MapData
from .weather import WeatherData
from .extra import ExtraLayers
from seacharts.core import files


class Environment:
    def __init__(self, settings: dict):
        self.scope = Scope(settings)
        self.parser = self.set_parser()
        files.build_directory_structure(self.scope.features, self.scope.resources, self.parser)
        self.map = MapData(self.scope, self.parser)
        self.weather = WeatherData(self.scope, self.parser)
        self.extra_layers = ExtraLayers(self.scope, self.parser)

        self.map.load_existing_shapefiles()
        if len(self.map.not_loaded_regions) > 0:
            self.map.parse_resources_into_shapefiles()

        if self.scope.type is MapFormat.S57:
            self.extra_layers.load_existing_shapefiles()
            if len(self.extra_layers.not_loaded_regions) > 0:
                self.extra_layers.parse_resources_into_shapefiles()

    def get_layers(self):
        return [
            *self.map.loaded_regions,
            *self.extra_layers.loaded_regions,
            ] 

    def set_parser(self) -> DataParser:
        if self.scope.type is MapFormat.S57:
            return S57Parser(self.scope.extent.bbox, self.scope.resources,
                             self.scope.extent.out_proj)
        elif self.scope.type is MapFormat.FGDB:
            return FGDBParser(self.scope.extent.bbox, self.scope.resources)
