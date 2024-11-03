"""
Contains the MapData class for containing parsed map (charts) data.
"""
from dataclasses import dataclass

from seacharts.layers import Layer, Land, Shore, Seabed
from .collection import ShapefileBasedCollection


@dataclass
class MapData(ShapefileBasedCollection):
    """
    Class for managing parsed map data including bathymetry, land, and shore layers.

    This class extends ShapefileBasedCollection to encapsulate the data related 
    to navigational charts. It initializes layers for land, shore, and 
    bathymetric data based on the specified depths.

    :param scope: The scope object that defines the depth levels and features 
                  relevant to the navigational charts.
    """
    def __post_init__(self):
        """
        Initializes the MapData instance by creating Seabed instances for each 
        depth specified in the scope. Also initializes land and shore layers.
        """
        self.bathymetry = {d: Seabed(depth=d) for d in self.scope.depths}
        self.land = Land()
        self.shore = Shore()

    @property
    def layers(self) -> list[Layer]:
        """
        Retrieves all layers associated with the map data.

        This includes the land layer, shore layer, and all bathymetry layers.

        :return: A list of Layer instances representing land, shore, and 
                 bathymetric data.
        """
        return [self.land, self.shore, *self.bathymetry.values()]

    @property
    def featured_regions(self) -> list[Layer]:
        """
        Retrieves the featured regions based on the specified features in the scope.

        This filters the layers to return only those that are recognized as 
        featured in the navigational charts.

        :return: A list of Layer instances that correspond to the featured 
                 regions defined in the scope.
        """
        return [x for x in self.layers if x.label in self.scope.features]
    
