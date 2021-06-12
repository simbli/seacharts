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
        self.safe_area = None
        self.ownship = None
        self.depth = None

    def create_ownship(self, x, y, heading, hull_scale, lon_scale, lat_scale):
        self.ownship = spl.Ship(
            x, y, heading, scale=hull_scale,
            lon_scale=lon_scale, lat_scale=lat_scale,
        )

    def filter_hazardous_areas(self, depth, buffer=0):
        if (not isinstance(depth, int)
                or depth not in self.scope.depths):
            raise ValueError(
                f"Danger area depth must be an integer from chosen depths: "
                f"{self.scope.depths}"
            )
        self.depth = depth
        if buffer < 0:
            raise ValueError(
                f"Buffer should be a positive integer."
            )
        self.safe_area = self.hydrography.bathymetry[depth]
        if buffer:
            self.safe_area.erode(buffer)
