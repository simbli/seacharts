from __future__ import annotations

import time
from abc import ABC
from dataclasses import dataclass, InitVar, field
from typing import List, Dict

import seacharts.environment.scope as env
from .base import Layer
from .layers import Seabed, Land, Shore


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

    def load(self, scope: env.Scope):
        layers = [x for x in self.layers if x.label in scope.layers]
        if scope.new_data:
            if scope.parser.verbose:
                print(
                    f"Processing {scope.extent.area // 10 ** 6} km^2 of "
                    f"{self.__class__.__name__} features from: "
                    + ', '.join(scope.files)
                )
            for layer in layers:
                start_time = time.time()
                records = layer.load_fgdb(scope.parser)
                info = f"{len(records)} {layer.name} geometries"

                if not records:
                    if scope.parser.verbose:
                        print(f"\rFound {info}.\n")
                    return

                if scope.parser.verbose:
                    print(f"\rMerging {info}...", end='')
                layer.unify(records)

                if scope.parser.verbose:
                    print(f"\rSimplifying {info}...", end='')
                layer.simplify(scope.tolerance)

                if scope.parser.verbose:
                    print(f"\rBuffering {info}...", end='')
                self.add_buffer(layer, scope.buffer)

                if scope.parser.verbose:
                    print(f"\rClipping {info}...", end='')
                layer.clip(scope.extent.bbox)

                layer.save(scope.parser)
                if scope.parser.verbose:
                    end_time = round(time.time() - start_time, 1)
                    print(
                        f"\rSaved {info} to shapefile in {end_time} seconds."
                    )

            if scope.parser.verbose:
                print()
        else:
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
