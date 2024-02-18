"""
Contains the DataParser class for spatial data parsing.
"""
import time
import warnings
from pathlib import Path
from typing import Generator

import fiona

from seacharts.core import paths
from seacharts.layers import labels, Layer


class DataParser:
    def __init__(
        self,
        bounding_box: tuple[int, int, int, int],
        path_strings: list[str],
    ):
        self.bounding_box = bounding_box
        self.paths = set([p.resolve() for p in (map(Path, path_strings))])
        self.paths.update(paths.default_resources)

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
        if not list(self._gdb_paths):
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
            records = self._load_from_fgdb(regions)
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
    def _gdb_paths(self) -> Generator[Path, None, None]:
        for path in self.paths:
            if not path.is_absolute():
                path = paths.cwd / path
            if self._is_gdb(path):
                yield path
            elif path.is_dir():
                for p in path.iterdir():
                    if self._is_gdb(p):
                        yield p

    def _load_from_fgdb(self, layer: Layer) -> list[dict]:
        depth = layer.depth if hasattr(layer, "depth") else 0
        external_labels = labels.NORWEGIAN_LABELS[layer.__class__.__name__]
        return list(self._read_fgdb(layer.label, external_labels, depth))

    def _parse_layers(
        self, path: Path, external_labels: list[str], depth: int
    ) -> Generator:
        for label in external_labels:
            if isinstance(label, dict):
                layer, depth_label = label["layer"], label["depth"]
                records = self._read_spatial_file(path, layer=layer)
                for record in records:
                    if record["properties"][depth_label] >= depth:
                        yield record
            else:
                yield from self._read_spatial_file(path, layer=label)

    def _read_fgdb(
        self, name: str, external_labels: list[str], depth: int
    ) -> Generator:
        for gdb_path in self._gdb_paths:
            records = self._parse_layers(gdb_path, external_labels, depth)
            yield from self._parse_records(records, name)

    def _read_shapefile(self, label: str) -> Generator:
        file_path = self._shapefile_path(label)
        if file_path.exists():
            yield from self._read_spatial_file(file_path)

    def _read_spatial_file(self, path: Path, **kwargs) -> Generator:
        try:
            with fiona.open(path, "r", **kwargs) as source:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    for record in source.filter(bbox=self.bounding_box):
                        yield record
        except ValueError as e:
            message = str(e)
            if "Null layer: " in message:
                message = f"Warning: {message[12:]} not found in data set."
            print(message)
        return

    def _shapefile_writer(self, file_path, geometry_type):
        return fiona.open(
            file_path,
            "w",
            schema=self._as_record("int", geometry_type),
            driver="ESRI Shapefile",
            crs={"init": "epsg:25833"},
        )

    def _write_to_shapefile(self, regions: Layer):
        geometry = regions.mapping
        file_path = self._shapefile_path(regions.label)
        with self._shapefile_writer(file_path, geometry["type"]) as sink:
            sink.write(self._as_record(regions.depth, geometry))

    @staticmethod
    def _as_record(depth, geometry):
        return {"properties": {"depth": depth}, "geometry": geometry}

    @staticmethod
    def _is_gdb(path: Path) -> bool:
        return path.is_dir() and path.suffix == ".gdb"

    @staticmethod
    def _parse_records(records, name):
        for i, record in enumerate(records):
            print(f"\rNumber of {name} records read: {i + 1}", end="")
            yield record
        return

    @staticmethod
    def _shapefile_path(label):
        return paths.shapefiles / label / (label + ".shp")
