from __future__ import annotations

import time
from abc import ABC
from dataclasses import InitVar, dataclass, field
from typing import Dict, List

import seacharts.environment.scope as env
from .base import Layer
from .layers import Land, Seabed, Shore


@dataclass
class _Hypsometry(ABC):
    scope: InitVar[env.Scope]

    def __post_init__(self, scope: env.Scope):
        raise NotImplementedError

    @property
    def layers(self) -> List[Layer]:
        raise NotImplementedError

    def add_buffer(self, layer, distance):
        raise NotImplementedError

    @property
    def loaded_layers(self) -> List[Layer]:
        return [layer for layer in self.layers if not layer.geometry.is_empty]

    @property
    def loaded(self) -> bool:
        return any(self.loaded_layers)

    def parse(self, scope: env.Scope):
        layers = [x for x in self.layers if x.label in scope.features]
        if not list(scope.parser.gdb_paths):
            return
        print(
            f"\nProcessing {scope.extent.area // 10 ** 6} km^2 of "
            f"{self.__class__.__name__} features:"
        )
        for layer in layers:
            start_time = time.time()
            records = layer.load_fgdb(scope.parser)
            info = f"{len(records)} {layer.name} geometries"

            if not records:
                print(f"\rFound {info}.")
                return
            else:
                print(f"\rMerging {info}...", end="")
                layer.unify(records)

                print(f"\rSimplifying {info}...", end="")
                layer.simplify(0)

                print(f"\rBuffering {info}...", end="")
                self.add_buffer(layer, 0)

                print(f"\rClipping {info}...", end="")
                layer.clip(scope.extent.bbox)

            layer.save(scope.parser)
            end_time = round(time.time() - start_time, 1)
            print(f"\rSaved {info} to shapefile in {end_time} s.")

    def load(self, scope: env.Scope):
        layers = [x for x in self.layers if x.label in scope.features]
        for layer in layers:
            layer.load_shapefile(scope.parser)


@dataclass
class Hydrography(_Hypsometry):
    bathymetry: Dict[int, Layer] = field(init=False)

    @property
    def layers(self):
        return [*self.bathymetry.values()]

    def __post_init__(self, scope: env.Scope):
        self.bathymetry = {d: Seabed(d) for d in scope.depths}
        self.load(scope)

    def add_buffer(self, layer, distance):
        layer.erode(distance)


@dataclass
class Topography(_Hypsometry):
    land: Land = field(init=False)
    shore: Shore = field(init=False)

    @property
    def layers(self):
        return [self.land, self.shore]

    def __post_init__(self, scope: env.Scope):
        self.land = Land()
        self.shore = Shore()
        self.load(scope)

    def add_buffer(self, layer, distance):
        layer.dilate(distance)
