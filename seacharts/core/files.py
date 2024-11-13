"""
Contains utility functions related to system files and directories.
"""
import csv, shutil
from collections.abc import Generator
from pathlib import Path
from seacharts.core.parser import DataParser
from . import paths


def verify_directory_exists(path_string: str) -> None:
    """
    Checks if a directory exists at the given path.

    If the directory does not exist, it prints a warning indicating whether the 
    path is absolute or relative.

    :param path_string: The path to the directory as a string.
    """
    path = Path(path_string)
    if not path.is_dir():
        path_type = "Absolute" if path.is_absolute() else "Relative"
        print(f"WARNING: {path_type} database path '{path}' not found.\n")


def build_directory_structure(features: list[str], resources: list[str], parser: DataParser) -> None:
    """
    Creates the directory structure for shapefiles and outputs based on the provided features 
    and resources. It also copies the initial configuration file to the map's shapefile directory.

    :param features: A list of feature names for which directories will be created.
    :param resources: A list of resource paths to validate and create directories for.
    :param parser: An instance of DataParser used to get the source root name.
    """
    map_dir_name = parser.get_source_root_name()
    paths.shapefiles.mkdir(exist_ok=True)
    paths.shapefiles =  paths.shapefiles / map_dir_name
    paths.output.mkdir(exist_ok=True)
    paths.shapefiles.mkdir(exist_ok=True)
    # shutil.copy(paths.config, paths.shapefiles) # used to save initial config

    for feature in features:
        shapefile_dir = paths.shapefiles / feature.lower()
        shapefile_dir.mkdir(parents=True, exist_ok=True)
    for resource in resources:
        path = Path(resource).resolve()
        if not path.suffix == ".gdb" or not path.suffix == ".000":
            path.mkdir(exist_ok=True)


def write_rows_to_csv(rows: list[tuple], file_path: Path) -> None:
    """
    Writes a list of rows to a CSV file at the specified path.

    Each row should be a tuple representing a single entry.

    :param rows: A list of tuples containing the data to write to the CSV file.
    :param file_path: The path where the CSV file will be created.
    """
    with open(file_path, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=",", lineterminator="\n")
        writer.writerows(rows)


def read_ship_poses() -> Generator[tuple]:
    """
    Reads ship positions from a CSV file and yields each position as a tuple.

    The first line of the CSV file is considered as a header and will be skipped.

    :return: A generator that yields tuples containing ship position data.
             Each tuple consists of (int id, int x, int y, float speed, list additional_data).
    """
    try:
        with open(paths.vessels) as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            _ = next(reader, None)
            rows = tuple(reader)
    except PermissionError or FileNotFoundError or StopIteration or RuntimeError:
        return
    for row in rows:
        if row:
            yield int(row[0]), int(row[1]), int(row[2]), float(row[3]), row[4:]
