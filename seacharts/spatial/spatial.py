from dataclasses import dataclass

from seacharts.environment.scope import Scope
from seacharts.layers import Layer, Land, Shore, Seabed


@dataclass
class SpatialData:
    scope: Scope

    def __post_init__(self):
        self.bathymetry = {d: Seabed(d) for d in self.scope.depths}
        self.land = Land()
        self.shore = Shore()

    def load_existing_shapefiles(self) -> None:
        self.scope.parser.load_shapefiles(self.featured_layers)
        if self.loaded:
            print("INFO: ENC created using data from existing shapefiles.\n")
        else:
            print("INFO: No existing spatial data was found.\n")

    def parse_resources_into_shapefiles(self) -> None:
        self.scope.parser.parse_resources(
            self.featured_layers, self.scope.resources, self.scope.extent.area
        )
        if self.loaded:
            print("\nENC update complete.\n")
        else:
            print("WARNING: Given spatial data source(s) seem empty.\n")

    @property
    def layers(self) -> list[Layer]:
        return [self.land, self.shore, *self.bathymetry.values()]

    @property
    def loaded_layers(self) -> list[Layer]:
        return [layer for layer in self.layers if not layer.geometry.is_empty]

    @property
    def featured_layers(self) -> list[Layer]:
        return [x for x in self.layers if x.label in self.scope.features]

    @property
    def loaded(self) -> bool:
        return any(self.loaded_layers)
