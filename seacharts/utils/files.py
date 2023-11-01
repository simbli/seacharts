"""
Contains file/directory related utility functions, such as functions for
writing to csv files.
"""
import csv
from pathlib import Path

from . import paths


def verify_directory_exists(path_string: str) -> None:
    path = Path(path_string)
    if not path.is_dir():
        path_type = "Absolute" if path.is_absolute() else "Relative"
        print(f"WARNING: {path_type} database path '{path}' not found.\n")


def build_directory_structure(features) -> None:
    paths.data.mkdir(exist_ok=True)
    paths.reports.mkdir(exist_ok=True)

    paths.db.mkdir(exist_ok=True)
    paths.hazards.mkdir(exist_ok=True)
    paths.paths.mkdir(exist_ok=True)
    paths.shapefiles.mkdir(exist_ok=True)

    paths.vessels.touch(exist_ok=True)
    paths.dynamic.touch(exist_ok=True)
    paths.static.touch(exist_ok=True)
    paths.path1.touch(exist_ok=True)
    paths.path2.touch(exist_ok=True)

    for feature in features:
        shapefile_dir = paths.shapefiles / feature.lower()
        shapefile_dir.mkdir(parents=True, exist_ok=True)


def write_rows_to_csv(rows, file_path) -> None:
    with open(file_path, "w") as csv_file:
        writer = csv.writer(csv_file, delimiter=",", lineterminator="\n")
        writer.writerows(rows)


def read_ship_poses():
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
