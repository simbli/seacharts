"""
Contains the DataCollection abstract class for containing parsed spatial data.
"""
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from seacharts.core import Scope, DataParser
from seacharts.layers import Layer


@dataclass
class DataCollection(ABC):
    scope: Scope
    parser: DataParser #= field(init=False)

    @property
    @abstractmethod
    def layers(self) -> list[Layer]:
        raise NotImplementedError

    @property
    def loaded_regions(self) -> list[Layer]:
        return [layer for layer in self.layers if not layer.geometry.is_empty]
    
    @property
    def not_loaded_regions(self) -> list[Layer]:
        return [layer for layer in self.layers if layer.geometry.is_empty]
    
    @property
    def loaded(self) -> bool:
        return any(self.loaded_regions)

@dataclass
class ShapefileBasedCollection(DataCollection, ABC):
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
