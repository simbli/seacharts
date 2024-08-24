import time
from pathlib import Path
from typing import Generator

import fiona

from seacharts.core import DataParser, paths
from seacharts.layers import Layer, labels


class FGDBParser(DataParser):

    def _load_from_file(self, layer: Layer) -> list[dict]:
        depth = layer.depth if hasattr(layer, "depth") else 0
        external_labels = labels.NORWEGIAN_LABELS[layer.__class__.__name__]
        return list(self._read_file(layer.label, external_labels, depth))

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

    @staticmethod
    def _parse_records(records, name):
        for i, record in enumerate(records):
            print(f"\rNumber of {name} records read: {i + 1}", end="")
            yield record
        return

    def _read_file(
        self, name: str, external_labels: list[str], depth: int
    ) -> Generator:
        for gdb_path in self._file_paths:
            records = self._parse_layers(gdb_path, external_labels, depth)
            yield from self._parse_records(records, name)

    def _is_map_type(self, path) -> bool:
        return path.is_dir() and path.suffix == ".gdb"
    
    def get_source_root_name(self) -> str:
        for path in self._file_paths:
            if self._is_map_type(path):
                return path.stem

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

    @staticmethod
    def _as_record(depth, geometry):
        return {"properties": {"depth": depth}, "geometry": geometry}

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
