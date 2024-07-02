"""
Contains the Extent class for defining details related to files of spatial data.
"""
from dataclasses import dataclass
from seacharts.core import files
from .extent import Extent
from .mapFormat import MapFormat

default_depths = [0, 1, 2, 5, 10, 20, 50, 100, 200, 350, 500] #TODO move to separate file


@dataclass
class Scope:

    def __init__(self, settings: dict):
        self.extent = Extent(settings)
        self.settings = settings
        self.resources = settings["enc"].get("resources", [])
        self.autosize = settings["enc"].get("autosize")

        self.depths = settings["enc"].get("depths", default_depths)
        self.features = ["land", "shore"]
        for depth in self.depths:
            self.features.append(f"seabed{depth}m")

        if settings["enc"].get("S57_layers", []):
            self.__s57_init(settings)
        else:
            self.type = MapFormat.FGDB

        self.weather = settings["enc"].get("weather", [])

        files.build_directory_structure(self.features, self.resources)

    # DEPARE --> depthsX - must be put into buffer dir first, then distributed between appropriate depths
    # LNDARE --> land
    # COALNE --> shore
    # remaining layers --> ?? separate dir for all or shared dir like "info"?
    def __s57_init(self, settings: dict):
        default_layers = ["LNDARE", "DEPARE", "COALNE"] #TODO move to separate file
        self.layers = settings["enc"].get("S57_layers", default_layers)
        self.type = MapFormat.S57

