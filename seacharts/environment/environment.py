"""
Contains the Environment class for collecting and manipulating loaded spatial data.
"""
import _warnings
from seacharts.core import Scope, MapFormat, S57Parser, FGDBParser, DataParser
from .map import MapData
from .weather import WeatherData
from .extra import ExtraLayers
from seacharts.core import files
from seacharts.layers import Layer

class Environment:
    """
    Environment class to manage spatial data resources, parsing, and loading layers 
    for ENC. This class handles the setup of various spatial data components 
    and supports loading additional layers, weather data, and different map formats.

    :param settings: A dictionary containing configuration settings for the environment.
    """
    def __init__(self, settings: dict):
        """
        Initializes the Environment instance with spatial data setup and parsing.
        :param settings: A dictionary of configuration settings used to initialize Scope.
        """

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

    def get_layers(self) -> list[Layer]:
        """
        Retrieves all loaded map and extra layers in the environment.
        
        :return: A list of all loaded layers, including both map and extra layers.
        """
        return [
            *self.map.loaded_regions,
            *self.extra_layers.loaded_regions,
            ] 
    
    def get_layer_by_name(self, layer_name: str) -> Layer | None:
        layer_name = layer_name.lower()
        layers = self.get_layers()
        for layer in layers:
            if layer.label == layer_name:
                return layer
        _warnings.warn(f"Layer {layer_name} not found in the enc!")
        return None
            

    def set_parser(self) -> DataParser:
        """
        Sets the appropriate parser based on the map format specified in the scope.

        :return: A DataParser instance specific to the map format (S57 or FGDB).
        :raises ValueError: If the map format is not supported.
        """
        if self.scope.type is MapFormat.S57:
            return S57Parser(self.scope.extent.bbox, self.scope.resources,
                             self.scope.extent.out_proj)
        elif self.scope.type is MapFormat.FGDB:
            return FGDBParser(self.scope.extent.bbox, self.scope.resources)
        else:
            raise ValueError("Unsupported map format")
