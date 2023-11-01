import warnings
from collections.abc import Generator
from pathlib import Path

import fiona

from . import paths


class ShapefileParser:
    def __init__(self, bounding_box, path_strings: list[str]):
        self.bounding_box = bounding_box
        self.paths = set([p.resolve() for p in (map(Path, path_strings))])

    def read_fgdb(self, label, external_labels, depth):
        for gdb_path in self.gdb_paths:
            records = self._parse_layers(gdb_path, external_labels, depth)
            yield from self._parse_records(records, label)

    def read_shapefile(self, label):
        file_path = self._shapefile_path(label)
        if file_path.exists():
            yield from self._read_spatial_file(file_path)

    def _parse_layers(self, path: Path, external_labels, depth):
        for label in external_labels:
            if isinstance(label, dict):
                layer, depth_label = label["layer"], label["depth"]
                records = self._read_spatial_file(path, layer=layer)
                for record in records:
                    if record["properties"][depth_label] >= depth:
                        yield record
            else:
                yield from self._read_spatial_file(path, layer=label)

    def _read_spatial_file(self, path: Path, **kwargs):
        with fiona.open(path, "r", **kwargs) as source:
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=RuntimeWarning)
                for record in source.filter(bbox=self.bounding_box):
                    yield record
        return

    @property
    def gdb_paths(self) -> Generator[Path]:
        for path in self.paths:
            if not path.is_absolute():
                path = paths.cwd / path
            if self._is_gdb(path):
                yield path
            elif path.is_dir():
                for p in path.iterdir():
                    if self._is_gdb(p):
                        yield p

    @staticmethod
    def _is_gdb(path: Path) -> bool:
        return path.is_dir() and path.suffix == ".gdb"

    @staticmethod
    def _parse_records(records, label):
        for i, record in enumerate(records):
            print(f"\rNumber of {label} records read: {i + 1}", end="")
            yield record
        return

    def write(self, shape):
        geometry = shape.mapping
        file_path = self._shapefile_path(shape.label)
        with self.writer(file_path, geometry["type"]) as sink:
            sink.write(self._as_record(shape.depth, geometry))

    def writer(self, file_path, geometry_type):
        return fiona.open(
            file_path,
            "w",
            schema=self._as_record("int", geometry_type),
            driver="ESRI Shapefile",
            crs={"init": "epsg:25833"},
        )

    @staticmethod
    def _depth_filter(depth_label, minimum_depth):
        return lambda r: r["properties"][depth_label] >= minimum_depth

    @staticmethod
    def _as_record(depth, geometry):
        return {"properties": {"depth": depth}, "geometry": geometry}

    @staticmethod
    def _shapefile_path(label):
        return paths.shapefiles / label / (label + ".shp")
