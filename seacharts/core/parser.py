"""
Contains the DataParser class for spatial data parsing.
"""
from abc import abstractmethod
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
        # self.paths.update(paths.default_resources)

    @staticmethod
    def _shapefile_path(label):
        return paths.shapefiles / label / (label + ".shp")

    @staticmethod
    def _shapefile_dir_path(label):
        return paths.shapefiles / label

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

    def _read_shapefile(self, label: str) -> Generator:
        file_path = self._shapefile_path(label)
        if file_path.exists():
            yield from self._read_spatial_file(file_path)

    def load_shapefiles(self, layers: list[Layer]) -> None:
        for layer in layers:
            records = list(self._read_shapefile(layer.label))
            layer.records_as_geometry(records)

    # main method for parsing corresponding map format
    @abstractmethod
    def parse_resources(
            self,
            regions_list: list[Layer],
            resources: list[str],
            area: float
    ) -> None:
        pass

    @abstractmethod
    def _is_map_type(self, path) -> bool:
        pass
    
    @abstractmethod
    def get_source_root_name(self) -> str:
        pass

    @property
    def _file_paths(self) -> Generator[Path, None, None]:
        for path in self.paths:
            if not path.is_absolute():
                path = Path.cwd() / path
            yield from self._get_files_recursive(path)
    
    def _get_files_recursive(self, path: Path) -> Generator[Path, None, None]:
        if self._is_map_type(path):
            yield path
        elif path.is_dir():
            for p in path.iterdir():
                yield from self._get_files_recursive(p)
