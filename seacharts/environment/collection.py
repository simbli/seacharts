"""
Contains the DataCollection abstract class for containing parsed spatial data.
"""
from abc import abstractmethod, ABC
from dataclasses import dataclass, field
from seacharts.core import Scope, DataParser
from seacharts.layers import Layer


@dataclass
class DataCollection(ABC):
    """
    Abstract base class for collections of parsed spatial data.

    This class serves as a blueprint for managing spatial data collections, 
    providing methods to retrieve loaded and unloaded regions.

    :param scope: The scope object defining the context and extent of the data collection.
    :param parser: The DataParser instance responsible for parsing the spatial data.
    """
    scope: Scope
    parser: DataParser

    @property
    @abstractmethod
    def layers(self) -> list[Layer]:
        """
        Abstract property that should return a list of layers contained in the data collection.

        :return: A list of Layer instances.
        """
        raise NotImplementedError

    @property
    def loaded_regions(self) -> list[Layer]:
        """
        Retrieves the regions that have been successfully loaded and contain geometry.

        :return: A list of loaded Layer instances (regions).
        """
        return [layer for layer in self.layers if not layer.geometry.is_empty]
    
    @property
    def not_loaded_regions(self) -> list[Layer]:
        """
        Retrieves the regions that have not been loaded or contain no geometry.

        :return: A list of Layer instances that are empty.
        """
        return [layer for layer in self.layers if layer.geometry.is_empty]
    
    @property
    def loaded(self) -> bool:
        """
        Checks if any regions in the collection have been loaded.

        :return: True if at least one region is loaded; otherwise, False.
        """
        return any(self.loaded_regions)

@dataclass
class ShapefileBasedCollection(DataCollection, ABC):
    """
    Abstract class for collections of spatial data that are based on shapefiles.

    This class provides methods for loading existing shapefiles and parsing 
    resources into shapefiles.

    :param scope: The scope object defining the context and extent of the data collection.
    :param parser: The DataParser instance responsible for parsing the spatial data.
    """
    def load_existing_shapefiles(self) -> None:
        """
        Loads existing shapefiles for the featured regions using the specified parser.

        If any spatial data is found, it prints a confirmation message; 
        otherwise, it indicates that no data was found.
        """
        for region in self.featured_regions:
            self.parser.load_shapefiles(region)
        if self.loaded:
            print("INFO: ENC created using data from existing shapefiles.\n")
        else:
            print("INFO: No existing spatial data was found.\n")

    def parse_resources_into_shapefiles(self) -> None:
        """
        Parses resources into shapefiles for regions that have not been loaded.

        This method utilizes the parser to process the resources defined in the scope 
        and updates the ENC based on the results. It prints a completion message 
        based on the loading status of the regions.
        """
        self.parser.parse_resources(
            self.not_loaded_regions, self.scope.resources, self.scope.extent.area
        )
        if self.loaded:
            print("\nENC update complete.\n")
        else:
            print("WARNING: Given spatial data source(s) seem empty.\n")
