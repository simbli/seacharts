"""
Contains depth-specific layer definitions used by the MapData container class.
"""
from dataclasses import dataclass

from seacharts.layers.layer import SingleDepthLayer, ZeroDepthLayer


@dataclass
class Seabed(SingleDepthLayer):
    ...


@dataclass
class Land(ZeroDepthLayer):
    ...


@dataclass
class Shore(ZeroDepthLayer):
    ...

@dataclass
class ExtraLayer(ZeroDepthLayer):
    tag:str = None
    @property
    def name(self) -> str:
        return self.tag
