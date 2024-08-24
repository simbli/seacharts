"""
Contains the MapData class for containing parsed map (charts) data.
"""
from dataclasses import dataclass

from seacharts.layers import Layer, Land, Shore, Seabed
from .collection import DataCollection, ShapefileBasedCollection


@dataclass
class MapData(ShapefileBasedCollection):
    def __post_init__(self):
        self.bathymetry = {d: Seabed(depth=d) for d in self.scope.depths}
        self.land = Land()
        self.shore = Shore()

    @property
    def layers(self) -> list[Layer]:
        return [self.land, self.shore, *self.bathymetry.values()]

    @property
    def featured_regions(self) -> list[Layer]:
        return [x for x in self.layers if x.label in self.scope.features]
    
