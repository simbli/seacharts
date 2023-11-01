from __future__ import annotations

from dataclasses import dataclass

import seacharts.utils as utils
from .extent import Extent


@dataclass
class Scope:
    def __init__(self, settings: dict, extent: Extent):
        self.extent: Extent = extent
        self.depths: list = settings["enc"].get("depths", [])
        self.files: list = settings["enc"].get("files", [])
        self.new_data = True
        self.layers = ["land", "shore"]
        for depth in self.depths:
            self.layers.append(f"seabed{depth}m")
        utils.files.build_directory_structure(self.layers)
        self.parser = utils.ShapefileParser(self.extent.bbox, self.files)
