"""
Contains the DataParser class for spatial data parsing.
"""
from abc import abstractmethod
import time
import warnings
from pathlib import Path
from typing import Generator

import fiona

from seacharts.core import paths
from seacharts.layers import Layer


class DataParser:
    def __init__(
        self,
        bounding_box: tuple[int, int, int, int],
        path_strings: list[str],
    ):
        self.bounding_box = bounding_box
        self.paths = set([p.resolve() for p in (map(Path, path_strings))])
        self.paths.update(paths.default_resources)

    #STAYS
    def load_shapefiles(self, layers: list[Layer]) -> None:
        for layer in layers:
            records = list(self._read_shapefile(layer.label))
            layer.records_as_geometry(records)

    def parse_resources(
            self,
            regions_list: list[Layer],
            resources: list[str],
            area: float
    ) -> None:
        if not list(self.paths):
            resources = sorted(list(set(resources)))
            if not resources:
                print("WARNING: No spatial data source location given in config.")
            else:
                message = "WARNING: No spatial data sources were located in\n"
                message += "         "
                resources = [f"'{r}'" for r in resources]
                message += ", ".join(resources[:-1])
                if len(resources) > 1:
                    message += f" and {resources[-1]}"
                print(message + ".")
            return
        print("INFO: Updating ENC with data from available resources...\n")
        print(f"Processing {area // 10 ** 6} km^2 of ENC features:")
        for regions in regions_list:
            start_time = time.time()
            records = self._load_from_file(regions)
            info = f"{len(records)} {regions.name} geometries"

            if not records:
                print(f"\rFound {info}.")
                return
            else:
                print(f"\rMerging {info}...", end="")
                regions.unify(records)

                print(f"\rSimplifying {info}...", end="")
                regions.simplify(0)

                print(f"\rBuffering {info}...", end="")
                regions.buffer(0)

                print(f"\rClipping {info}...", end="")
                regions.clip(self.bounding_box)

            self._write_to_shapefile(regions)
            end_time = round(time.time() - start_time, 1)
            print(f"\rSaved {info} to shapefile in {end_time} s.")

    @property
    def _file_paths(self) -> Generator[Path, None, None]:
        for path in self.paths:
            if not path.is_absolute():
                path = paths.cwd / path
            if self._is_map_type(path):
                yield path
            elif path.is_dir():
                for p in path.iterdir():
                    if self._is_map_type(p):
                        yield p

    @abstractmethod
    def _is_map_type(self, path) -> bool:
        pass

    @abstractmethod
    def _load_from_file(self, layer: Layer) -> list[dict]:
        pass

    @abstractmethod
    def _parse_layers(
        self, path: Path, external_labels: list[str], depth: int
    ) -> Generator:
        pass

    @abstractmethod
    def _read_file(
        self, name: str, external_labels: list[str], depth: int
    ) -> Generator:
        pass

    #STAYS
    def _read_shapefile(self, label: str) -> Generator:
        file_path = self._shapefile_path(label)
        if file_path.exists():
            yield from self._read_spatial_file(file_path)

    #STAYS
    def _read_spatial_file(self, path: Path, **kwargs) -> Generator:
        try:
            with fiona.open(path, "r", **kwargs) as source:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    for record in source.filter(bbox=self.bounding_box): #TODO: auto coordinates
                        yield record
        except ValueError as e:
            message = str(e)
            if "Null layer: " in message:
                message = f"Warning: {message[12:]} not found in data set."
            print(message)
        return

    def _shapefile_writer(self, file_path, geometry_type): #TODO rozbic
        return fiona.open(
            file_path,
            "w",
            schema=self._as_record("int", geometry_type),
            driver="ESRI Shapefile",
            crs={"init": "epsg:25833"},
        )

    def _write_to_shapefile(self, regions: Layer): #TODO rozbic
        geometry = regions.mapping
        file_path = self._shapefile_path(regions.label)
        with self._shapefile_writer(file_path, geometry["type"]) as sink:
            sink.write(self._as_record(regions.depth, geometry))

    @staticmethod
    def _as_record(depth, geometry):
        return {"properties": {"depth": depth}, "geometry": geometry}

    @staticmethod
    def _parse_records(records, name):
        for i, record in enumerate(records):
            print(f"\rNumber of {name} records read: {i + 1}", end="")
            yield record
        return

    #STAYS
    @staticmethod
    def _shapefile_path(label):
        return paths.shapefiles / label / (label + ".shp")

