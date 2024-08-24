from seacharts.layers import ExtraLayer
from seacharts.layers.layer import Layer
from .collection import ShapefileBasedCollection
from dataclasses import dataclass

@dataclass
class ExtraLayers(ShapefileBasedCollection):
    
    def __post_init__(self):
        self.extra_layers : list[ExtraLayer] = []
        for tag, color in self.scope.extra_layers.items():
            self.extra_layers.append(ExtraLayer(tag=tag, color=color))

    @property
    def layers(self) -> list[Layer]:
        return self.extra_layers
    
    @property
    def featured_regions(self) -> list[Layer]:
        return [x for x in self.layers if x.tag in self.scope.extra_layers.keys()]
