from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import seacharts.spatial as spl
import seacharts.utils as utils

from .extent import Extent


@dataclass
class Scope:
    def __init__(self, settings: dict, extent: Extent):
        self.extent: Extent = extent
        self.buffer: int = settings["enc"]["buffer"]
        self.tolerance: int = settings["enc"]["tolerance"]
        self.layers: list = settings["enc"]["layers"]
        self.depths: list = settings["enc"]["depths"]
        self.files: list = settings["enc"]["files"]
        self.new_data: bool = settings["enc"]["new_data"]
        self.raw_data: bool = settings["enc"]["raw_data"]
        self.border: bool = settings["enc"]["border"]
        self.verbose: bool = settings["enc"]["verbose"]

        utils.files.build_directory_structure()

        seabed = spl.supported_layers[0].lower()
        if seabed in self.layers:
            self.layers.remove(seabed)
            for depth in self.depths:
                self.layers.append(f"{seabed}{depth}m")

        utils.files.build_directory_structure(self.layers)

        self.parser: utils.parser.ShapefileParser = utils.ShapefileParser(self.extent.bbox, self.files, self.verbose)
