"""
Contains depth-specific layer definitions used by the MapData container class.
"""
from dataclasses import dataclass

from seacharts.layers.layer import SingleDepthLayer, ZeroDepthLayer


@dataclass
class Seabed(SingleDepthLayer):
    """Layer representing seabed geometries at a single depth."""
    ...


@dataclass
class Land(ZeroDepthLayer):
    """Layer representing land geometries at zero depth."""
    ...


@dataclass
class Shore(ZeroDepthLayer):
    """Layer representing shore geometries at zero depth."""
    ...

@dataclass
class ExtraLayer(ZeroDepthLayer):
    """
    Class for defining extra layers with additional attributes.

    :param tag: A tag associated with the extra layer - originates from S57 tags, will be later treated as name.
    """
    tag:str = None
    @property
    def name(self) -> str:
        return self.tag
