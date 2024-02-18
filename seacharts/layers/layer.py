from __future__ import annotations

from abc import ABC
from dataclasses import dataclass

from shapely import geometry as geo

from seacharts.spatial.base import Shape


@dataclass
class Layer(Shape, ABC):
    @property
    def _external_labels(self) -> list[str]:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__

    @property
    def label(self) -> str:
        return self.name.lower()

    def records_as_geometry(self, records: list[dict]) -> None:
        if len(records) > 0:
            self.geometry = self._record_to_geometry(records[0])
            if isinstance(self.geometry, geo.Polygon):
                self.geometry = self.as_multi(self.geometry)

    def unify(self, records: list[dict]) -> None:
        geometries = [self._record_to_geometry(r) for r in records]
        self.geometry = self.collect(geometries)


@dataclass
class ZeroDepth:
    depth = 0


@dataclass
class SingleDepth:
    depth: int


@dataclass
class MultiDepth:
    @property
    def depth(self) -> None:
        raise AttributeError("Multi-depth shapes have no single depth.")
