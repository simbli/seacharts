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
        autosize: bool
    ):
        self.bounding_box = bounding_box
        self.paths = set([p.resolve() for p in (map(Path, path_strings))])
        self.paths.update(paths.default_resources)
        self.autosize = autosize

    @staticmethod
    def _shapefile_path(label):
        return paths.shapefiles / label / (label + ".shp")

    @staticmethod
    def _shapefile_dir_path(label):
        return paths.shapefiles / label

    ######LOADING SHAPEFILES#####
    def _read_spatial_file(self, path: Path, **kwargs) -> Generator:
        try:
            with fiona.open(path, "r", **kwargs) as source:
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore", category=RuntimeWarning)
                    if self.autosize is True: #TODO: Extend in Scope needs to be updated according to record sizes when using autosize
                        for record in source:
                            yield record
                    else:
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

    ######LOADING SHAPEFILES#####
    @abstractmethod
    def parse_resources(
            self,
            regions_list: list[Layer],
            resources: list[str],
            area: float
    ) -> None:
        pass  #main method for parsing corresponding map format

    @abstractmethod
    def _is_map_type(self, path) -> bool:
        pass    #method for detecting files/directories containing corresponding map format

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





