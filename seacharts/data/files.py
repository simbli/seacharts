import csv

from . import paths as path


def verify_directory_exists(dir_path):
    if not (path.external / dir_path).is_dir():
        raise FileNotFoundError(
            f"Folder {dir_path} not found at:\r\n{path.external}."
        )


def build_directory_structure(features):
    path.reports.mkdir(parents=True, exist_ok=True)
    path.external.mkdir(parents=True, exist_ok=True)
    path.shapefiles.mkdir(parents=True, exist_ok=True)
    path.frames_dir.mkdir(parents=True, exist_ok=True)
    for feature in features:
        shapefile_dir = path.shapefiles / feature.lower()
        shapefile_dir.mkdir(parents=True, exist_ok=True)


def write_rows_to_csv(rows):
    with open(path.vessels, 'w') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerows(rows)


def read_ship_poses():
    try:
        with open(path.vessels) as csv_file:
            reader = csv.reader(csv_file, delimiter=',')
            _ = next(reader)
            rows = tuple(reader)
    except PermissionError or FileNotFoundError or StopIteration:
        return
    for row in rows:
        if row:
            yield int(row[0]), int(row[1]), int(row[2]), float(row[3]), row[4]
