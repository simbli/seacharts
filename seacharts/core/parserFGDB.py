import time
from pathlib import Path
from typing import Generator

from seacharts.core import DataParser, paths
from seacharts.layers import Layer, labels


class FGDBParser(DataParser):

    def _load_from_file(self, layer: Layer) -> list[dict]:
        depth = layer.depth if hasattr(layer, "depth") else 0
        external_labels = labels.NORWEGIAN_LABELS[layer.__class__.__name__]
        return list(self._read_file(layer.label, external_labels, depth))

    def _read_file(
        self, name: str, external_labels: list[str], depth: int
    ) -> Generator:
        for gdb_path in self._file_paths:
            records = self._parse_layers(gdb_path, external_labels, depth)
            yield from self._parse_records(records, name)

    def _is_map_type(self, path):
        return path.is_dir() and path.suffix is ".gdb"

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

