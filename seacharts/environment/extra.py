from seacharts.layers import ExtraLayer
from seacharts.layers.layer import Layer
from .collection import DataCollection
from dataclasses import dataclass

@dataclass
class ExtraLayers(DataCollection):
    
    def __post_init__(self):
        self.extra_layers : list[ExtraLayer] = []
        for tag, color in self.scope.extra_layers.items():
            self.extra_layers.append(ExtraLayer(tag=tag, color=color))

    @property
    def layers(self) -> list[Layer]:
        return self.extra_layers

    def load_existing_shapefiles(self) -> None:
        self.parser.load_shapefiles(self.featured_regions)
        if self.loaded:
            print("INFO: ENC created using data from existing shapefiles.\n")
        else:
            print("INFO: No existing spatial data was found.\n")

    def parse_resources_into_shapefiles(self) -> None:
        self.parser.parse_resources(
            self.not_loaded_regions, self.scope.resources, self.scope.extent.area
        )
        if self.loaded:
            print("\nENC update complete.\n")
        else:
            print("WARNING: Given spatial data source(s) seem empty.\n")

    @property
    def loaded(self) -> bool:
        return any(self.loaded_regions)

    @property
    def loaded_regions(self) -> list[Layer]:
        return [layer for layer in self.layers if not layer.geometry.is_empty]
    
    @property
    def not_loaded_regions(self) -> list[Layer]:
        return [layer for layer in self.layers if layer.geometry.is_empty]
    
    @property
    def featured_regions(self) -> list[Layer]:
        return [x for x in self.layers if x.tag in self.scope.extra_layers.keys()]
