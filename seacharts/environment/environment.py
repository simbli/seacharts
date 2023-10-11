from __future__ import annotations

import seacharts.spatial as spl

from .extent import Extent
from .scope import Scope


class Environment:
    supported_layers = ", ".join(spl.supported_layers)

    def __init__(self, settings: dict):
        self.supported_crs = "EUREF89 UTM zone " + str(settings["enc"]["utm_zone"])
        extent = Extent(settings)
        self.scope = Scope(settings, extent)
        self.hydrography = spl.Hydrography(self.scope)
        self.topography = spl.Topography(self.scope)
        self.safe_area = None
        self.ownship = None
        self.depth = None

    def create_ownship(self, x, y, heading, hull_scale, lon_scale, lat_scale) -> None:
        self.ownship = spl.Ship(
            x,
            y,
            heading,
            scale=hull_scale,
            lon_scale=lon_scale,
            lat_scale=lat_scale,
        )

    def filter_hazardous_areas(self, depth, buffer=0) -> None:
        if not isinstance(depth, int) or depth not in self.scope.depths:
            raise ValueError("Danger area depth must be an integer from chosen depths: " f"{self.scope.depths}")
        self.depth = depth
        if buffer < 0:
            raise ValueError("Buffer should be a positive integer.")
        self.safe_area = self.hydrography.bathymetry[depth]
        if buffer:
            self.safe_area.erode(buffer)
