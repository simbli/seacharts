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
    parser: DataParser = field(init=False)

    @property
    @abstractmethod
    def layers(self) -> list[Layer]:
        raise NotImplementedError
