from __future__ import annotations

from typing import List, Tuple

import seacharts.spatial as spl
from .extent import Extent
from .scope import Scope


class Environment:
    supported_crs = "EUREF89 UTM zone 33"
    supported_layers = ", ".join(spl.supported_layers)

    def __init__(self,
                 size: Tuple[int, int] = None,
                 origin: Tuple[int, int] = None,
                 center: Tuple[int, int] = None,
                 buffer: int = None,
                 tolerance: int = None,
                 layers: List[str] = None,
                 depths: List[int] = None,
                 files: List[str] = None,
                 new_data: bool = None,
                 verbose: bool = None,
                 ):
        extent = Extent(size, origin, center)
        self.scope = Scope(
            extent, buffer, tolerance, layers, depths, files, new_data, verbose
        )
        self.hydrography = spl.Hydrography(self.scope)
        self.topography = spl.Topography(self.scope)
