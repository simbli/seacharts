from seacharts.layers import ExtraLayer
from seacharts.layers.layer import Layer
from .collection import ShapefileBasedCollection
from dataclasses import dataclass
"""
Contains the ExtraLayers class for managing additional layers from S57 maps (may be expanded for other formats in the future).
"""
@dataclass
class ExtraLayers(ShapefileBasedCollection):
    """
    Class for managing extra layers derived from S57 maritime maps.

    This class extends the ShapefileBasedCollection to handle additional layers 
    specified in the scope, enabling the loading and processing of extra layers 
    such as those beyond the standard DEPARE, LNDARE, and COALNE (stored in respectively: bathymetry, land and shoreline).

    :param scope: The scope object that includes information about extra layers 
                  and their corresponding colors.
    """
    def __post_init__(self):
        """
        Initializes the ExtraLayers instance by creating ExtraLayer instances 
        based on the extra layer specifications in the scope.
        """
        self.extra_layers : list[ExtraLayer] = []
        for tag, color in self.scope.extra_layers.items():
            self.extra_layers.append(ExtraLayer(tag=tag, color=color))

    @property
    def layers(self) -> list[Layer]:
        """
        Retrieves the list of extra layers.

        :return: A list of ExtraLayer instances that have been initialized 
                 from the scope.
        """
        return self.extra_layers
    
    @property
    def featured_regions(self) -> list[Layer]:
        """
        Retrieves the featured regions that are included in the extra layers.

        This property filters the layers to return only those that are 
        recognized as featured based on their tags in the scope.

        :return: A list of Layer instances that correspond to the featured 
                 regions defined in the extra layers.
        """
        return [x for x in self.layers if x.tag in self.scope.extra_layers.keys()]
