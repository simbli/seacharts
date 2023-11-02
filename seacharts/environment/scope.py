from __future__ import annotations

from dataclasses import dataclass

import seacharts.utils as utils
from .extent import Extent


@dataclass
class Scope:
    def __init__(self, settings: dict):
        self.extent = Extent(settings)
        self.depths = settings["enc"].get("depths", [])
        self.resources = settings["enc"].get("resources", [])
        self.parser = utils.ShapefileParser(self.extent.bbox, self.resources)
        self.features = ["land", "shore"]
        for depth in self.depths:
            self.features.append(f"seabed{depth}m")
        utils.files.build_directory_structure(self.features, self.resources)
