from __future__ import annotations

import seacharts.spatial as spl
from .extent import Extent
from .scope import Scope


class Environment:
    supported_layers = ", ".join(spl.supported_layers)

    def __init__(self, settings: dict):
        extent = Extent(settings)
        self.scope = Scope(settings, extent)
        self.hydrography = spl.Hydrography(self.scope)
        self.topography = spl.Topography(self.scope)
        self.safe_area = None
        self.ownship = None
        self.depth = None
