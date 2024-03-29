"""
Contains the Extent class for defining details related to files of spatial data.
"""
from dataclasses import dataclass

from seacharts.core import files
from .extent import Extent


@dataclass
class Scope:
    default_depths = [0, 1, 2, 5, 10, 20, 50, 100, 200, 350, 500]

    def __init__(self, settings: dict):
        self.extent = Extent(settings)
        self.depths = settings["enc"].get("depths", self.default_depths)
        self.resources = settings["enc"].get("resources", [])
        self.features = ["land", "shore"]
        for depth in self.depths:
            self.features.append(f"seabed{depth}m")
        files.build_directory_structure(self.features, self.resources)
