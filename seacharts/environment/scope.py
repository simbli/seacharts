from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import seacharts.data as data
import seacharts.spatial as spl
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
    verbose: bool = None
    parser: data.parser.ShapefileParser = field(init=False)

    def __post_init__(self):
        defaults = data.config.read_settings()

        key = 'buffer'
        if self.buffer is None:
            default = data.config.parse(key, defaults)
            self.buffer = int(default[0])
            data.config.validate(key, self.buffer, int)
        if self.buffer < 1:
            raise ValueError(
                f"Buffer should be a strictly positive integer."
            )

        key = 'tolerance'
        if self.tolerance is None:
            default = data.config.parse(key, defaults)
            self.tolerance = int(default[0])
        data.config.validate(key, self.tolerance, int)
        if self.tolerance < 1:
            raise ValueError(
                f"Tolerance should be a strictly positive integer."
            )

        key = 'layers'
        if self.layers is None:
            self.layers = data.config.parse(key, defaults)
        data.config.validate(key, self.layers, list, str)
        for layer in self.layers:
            if layer.capitalize() not in spl.supported_layers:
                raise ValueError(
                    f"Feature '{layer}' not supported, "
                    f"possible candidates are: {spl.supported_layers}"
                )

        key = 'depths'
        if self.depths is None:
            default = data.config.parse(key, defaults)
            self.depths = [int(v) for v in default]
        data.config.validate(key, self.depths, list, int)
        if any(d < 0 for d in self.depths):
            raise ValueError(
                f"Depth bins should be non-negative."
            )
        self.depths.sort()

        key = 'files'
        if self.files is None:
            self.files = data.config.parse(key, defaults)
        data.config.validate(key, self.files, list, str)
        for file_name in self.files:
            data.files.verify_directory_exists(file_name)

        key = 'new_data'
        if self.new_data is None:
            default = data.config.parse(key, defaults)
            self.new_data = bool(int(default[0]))
        data.config.validate(key, self.new_data, bool)

        key = 'verbose'
        if self.verbose is None:
            default = data.config.parse(key, defaults)
            self.verbose = bool(int(default[0]))
        data.config.validate(key, self.verbose, bool)

        data.config.save(dict(
            size=self.extent.size,
            center=self.extent.center,
            buffer=self.buffer,
            tolerance=self.tolerance,
            layers=self.layers,
            depths=self.depths,
            files=self.files,
            new_data=int(self.new_data),
            verbose=int(self.verbose),
        ))

        seabed = spl.supported_layers[0].lower()
        if seabed in self.layers:
            self.layers.remove(seabed)
            for depth in self.depths:
                self.layers.append(f"{seabed}{depth}m")
        data.files.build_directory_structure(self.layers)

        self.parser = data.ShapefileParser(
            self.extent.bbox, self.files, self.verbose
        )
