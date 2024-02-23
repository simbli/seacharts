"""
Contains the Extent class for defining details related to files of spatial data.
"""
from dataclasses import dataclass
from enum import Enum, auto

from seacharts.core import files
from .extent import Extent


class MapFormat(Enum):
    FGDB = auto()
    S57 = auto()


@dataclass
class Scope:
    def __init__(self, settings: dict):
        self.extent = Extent(settings)
        self.resources = settings["enc"].get("resources", [])

        if settings["enc"].get("FGDB_depths",[]):
            self.__fgdb_init(settings)
        elif settings["enc"].get("S57_layers", []):
            self.__s57_init(settings)

        files.build_directory_structure(self.features, self.resources)

    def __fgdb_init(self, settings: dict):
        default_depths = [0, 1, 2, 5, 10, 20, 50, 100, 200, 350, 500]
        self.depths = settings["enc"].get("FGDB_depths", default_depths)
        self.features = ["land", "shore"]
        for depth in self.depths:
            self.features.append(f"seabed{depth}m")
        self.type = MapFormat.FGDB

    def __s57_init(self, settings: dict):
        default_layers = ["LNDARE", "DEPARE"] #TODO: double-check desired default layers
        self.features = settings["enc"].get("S57_layers", default_layers)
        self.type = MapFormat.S57

