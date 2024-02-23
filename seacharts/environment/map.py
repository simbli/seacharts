"""
Contains the MapData class for containing parsed map (charts) data.
"""
from dataclasses import dataclass

from seacharts.core import DataParser
from seacharts.layers import Layer, Land, Shore, Seabed
from .collection import DataCollection


@dataclass
class MapData(DataCollection):
    def __post_init__(self):
        self.bathymetry = {d: Seabed(d) for d in self.scope.depths}
        self.land = Land()
        self.shore = Shore()


    def load_existing_shapefiles(self) -> None:
        self.parser.load_shapefiles(self.featured_regions)
        if self.loaded:
            print("INFO: ENC created using data from existing shapefiles.\n")
        else:
            print("INFO: No existing spatial data was found.\n")

    def parse_resources_into_shapefiles(self) -> None:
        self.parser.parse_resources(
            self.featured_regions, self.scope.resources, self.scope.extent.area
        )
        if self.loaded:
            print("\nENC update complete.\n")
        else:
            print("WARNING: Given spatial data source(s) seem empty.\n")

    @property
    def layers(self) -> list[Layer]:
        return [self.land, self.shore, *self.bathymetry.values()]

    @property
    def loaded(self) -> bool:
        return any(self.loaded_regions)

    @property
    def loaded_regions(self) -> list[Layer]:
        return [layer for layer in self.layers if not layer.geometry.is_empty]

    @property
    def featured_regions(self) -> list[Layer]:
        return [x for x in self.layers if x.label in self.scope.features]
