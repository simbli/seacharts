import time
from abc import ABC
from dataclasses import InitVar, dataclass, field

from .base import Layer
from .layers import Land, Seabed, Shore
from ..environment.scope import Scope


@dataclass
class _Hypsometry(ABC):
    scope: InitVar[Scope]

    def __post_init__(self, scope: Scope):
        raise NotImplementedError

    @property
    def layers(self) -> list[Layer]:
        raise NotImplementedError

    @property
    def loaded_layers(self) -> list[Layer]:
        return [layer for layer in self.layers if not layer.geometry.is_empty]

    @property
    def loaded(self) -> bool:
        return any(self.loaded_layers)

    def parse(self, scope: Scope) -> None:
        layers = [x for x in self.layers if x.label in scope.features]
        if not list(scope.parser.gdb_paths):
            return
        print(
            f"\nProcessing {scope.extent.area // 10 ** 6} km^2 of "
            f"{self.__class__.__name__} features:"
        )
        for layer in layers:
            start_time = time.time()
            records = scope.parser.load_fgdb(layer)
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
                layer.buffer(0)

                print(f"\rClipping {info}...", end="")
                layer.clip(scope.extent.bbox)

            scope.parser.save(layer)
            end_time = round(time.time() - start_time, 1)
            print(f"\rSaved {info} to shapefile in {end_time} s.")

    def load(self, scope: Scope) -> None:
        layers = [x for x in self.layers if x.label in scope.features]
        for layer in layers:
            records = scope.parser.load_shapefile(layer)
            layer.records_as_geometry(records)


@dataclass
class Hydrography(_Hypsometry):
    bathymetry: dict[int, Layer] = field(init=False)

    @property
    def layers(self) -> list[Layer]:
        return [*self.bathymetry.values()]

    def __post_init__(self, scope: Scope):
        self.bathymetry = {d: Seabed(d) for d in scope.depths}


@dataclass
class Topography(_Hypsometry):
    land: Land = field(init=False)
    shore: Shore = field(init=False)

    @property
    def layers(self) -> list[Layer]:
        return [self.land, self.shore]

    def __post_init__(self, scope: Scope):
        self.land = Land()
        self.shore = Shore()
