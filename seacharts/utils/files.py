"""Contains file/directory related utility functions, such as functions for writing to csv files."""
import csv

from . import paths as path


def verify_directory_exists(dir_path) -> None:
    if not (path.external / dir_path).is_dir():
        raise FileNotFoundError(
            f"Folder {dir_path} not found at:\r\n{path.external}."
        )


def build_directory_structure(features=None) -> None:
    if features is None:
        path.data.mkdir(exist_ok=True)
        path.reports.mkdir(exist_ok=True)

        path.external.mkdir(exist_ok=True)
        path.hazards.mkdir(exist_ok=True)
        path.paths.mkdir(exist_ok=True)
        path.shapefiles.mkdir(exist_ok=True)

        path.vessels.touch(exist_ok=True)
        path.dynamic.touch(exist_ok=True)
        path.static.touch(exist_ok=True)
        path.path1.touch(exist_ok=True)
        path.path2.touch(exist_ok=True)
    else:
        for feature in features:
            shapefile_dir = path.shapefiles / feature.lower()
            shapefile_dir.mkdir(parents=True, exist_ok=True)


def write_rows_to_csv(rows, file_path) -> None:
    with open(file_path, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', lineterminator='\n')
        writer.writerows(rows)


def read_ship_poses():
    try:
        with open(path.vessels) as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            _ = next(reader, None)
            rows = tuple(reader)
    except (PermissionError or FileNotFoundError
            or StopIteration or RuntimeError):
        return
    for row in rows:
        if row:
            yield int(row[0]), int(row[1]), int(row[2]), float(row[3]), row[4:]
