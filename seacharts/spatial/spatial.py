from abc import abstractmethod, ABC
from dataclasses import dataclass

from seacharts.environment.scope import Scope
from seacharts.layers import Layer


@dataclass
class SpatialData(ABC):
    scope: Scope

    @property
    @abstractmethod
    def layers(self) -> list[Layer]:
        raise NotImplementedError
