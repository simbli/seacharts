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
    """
    Base class for parsing spatial data sources, providing common functionality for 
    file handling and shapefile processing.

    :param bounding_box: Tuple defining bounding box coordinates as (xmin, ymin, xmax, ymax).
    :param path_strings: List of paths to spatial data sources.
    """
    def __init__(
        self,
        bounding_box: tuple[int, int, int, int],
        path_strings: list[str],
    ):
        self.bounding_box = bounding_box
        self.paths = set([p.resolve() for p in (map(Path, path_strings))])

    @staticmethod
    def _shapefile_path(label):
        """
        Constructs the path for a shapefile based on the given label.

        :param label: The label of the shapefile.
        :return: Path to the shapefile.
        """
        return paths.shapefiles / label / (label + ".shp")

    @staticmethod
    def _shapefile_dir_path(label):
        """
        Constructs the directory path for shapefiles based on the given label.

        :param label: The label of the shapefile directory.
        :return: Path to the shapefile directory.
        """
        return paths.shapefiles / label

    def _read_spatial_file(self, path: Path, **kwargs) -> Generator:
        """
        Reads a spatial file (shapefile) and yields records that fall within the bounding box.

        :param path: Path to the spatial file to be read.
        :param kwargs: Additional arguments for reading the file.
        :yield: Records from the spatial file that are within the bounding box.
        """
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
        """
        Reads records from a specified shapefile if it exists.

        :param label: Label of the shapefile to read.
        :yield: Records from the shapefile if it exists.
        """
        file_path = self._shapefile_path(label)
        if file_path.exists():
            yield from self._read_spatial_file(file_path)

    def load_shapefiles(self, layer: Layer) -> None:
        """
        Loads records from shapefiles into the specified layer.

        :param layer: Layer object to load the records into.
        """
        records = list(self._read_shapefile(layer.label))
        layer.records_as_geometry(records)
        layer.records= records
        

    def _valid_paths_and_resources(self, paths: set[Path], resources: list[str], area: float)-> bool:
        """
        Validates the provided paths and resources, checking if they exist and are usable.

        :param paths: Set of paths to validate.
        :param resources: List of resource names to validate.
        :param area: Area being processed, used for logging.
        :return: True if paths and resources are valid, otherwise False.
        """
        if not list(paths):
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
            return False
        else:
            print("INFO: Updating ENC with data from available resources...\n")
            print(f"Processing {area // 10 ** 6} km^2 of ENC features:")
            return True
        
    # main method for parsing corresponding map format
    @abstractmethod
    def parse_resources(
            self,
            regions_list: list[Layer],
            resources: list[str],
            area: float
    ) -> None:
        """
        Abstract method for parsing resources, to be implemented by subclasses.

        :param regions_list: List of Layer objects representing different regions to be processed.
        :param resources: List of resource paths to be considered for processing.
        :param area: Area of the region being processed.
        """
        pass

    @abstractmethod
    def _is_map_type(self, path) -> bool:
        """
        Abstract method to check if the provided path corresponds to a valid map type.

        :param path: Path to be checked.
        :return: True if the path is a valid map type, otherwise False.
        """
        pass
    
    @abstractmethod
    def get_source_root_name(self) -> str:
        """
        Abstract method to retrieve the root name of the source data.

        :return: The root name of the source data.
        """
        pass

    @property
    def _file_paths(self) -> Generator[Path, None, None]:
        """
        Generator that yields valid file paths from the configured paths.

        :yield: Valid file paths for spatial data sources.
        """
        for path in self.paths:
            if not path.is_absolute():
                path = Path.cwd() / path
            yield from self._get_files_recursive(path)
    
    def _get_files_recursive(self, path: Path) -> Generator[Path, None, None]:
        """
        Recursively retrieves valid file paths for the specified path.

        :param path: Path to be searched for valid files.
        :yield: Valid file paths found in the directory.
        """
        if self._is_map_type(path):
            yield path
        elif path.is_dir():
            for p in path.iterdir():
                yield from self._get_files_recursive(p)
