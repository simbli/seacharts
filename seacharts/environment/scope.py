from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import seacharts.spatial as spl
import seacharts.utils as utils

from .extent import Extent


@dataclass
class Scope:
    extent: Extent
    buffer: int = None
    tolerance: int = None
    layers: List[str] = None
    depths: List[int] = None
    files: List[str] = None
    new_data: bool = None
    raw_data: bool = None
    border: bool = None
    verbose: bool = None
    parser: utils.parser.ShapefileParser = field(init=False)

    def __init__(self, settings: dict, extent: Extent):
        self.extent = extent
        self.buffer = settings['enc']['buffer']
        self.tolerance = settings['enc']['tolerance']
        self.layers = settings['enc']['layers']
        self.depths = settings['enc']['depths']
        self.files = settings['enc']['files']
        self.new_data = settings['enc']['new_data']
        self.raw_data = settings['enc']['raw_data']
        self.border = settings['enc']['border']
        self.verbose = settings['enc']['verbose']

        utils.files.build_directory_structure()

        seabed = spl.supported_layers[0].lower()
        if seabed in self.layers:
            self.layers.remove(seabed)
            for depth in self.depths:
                self.layers.append(f"{seabed}{depth}m")

        utils.files.build_directory_structure(self.layers)

        self.parser = utils.ShapefileParser(
            self.extent.bbox, self.files, self.verbose
        )
