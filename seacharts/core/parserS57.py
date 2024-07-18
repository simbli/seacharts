import os.path
import subprocess
import time
from pathlib import Path

from seacharts.core import DataParser
from seacharts.layers import Layer, Land, Shore, Seabed


class S57Parser(DataParser):
    def __init__(
            self,
            bounding_box: tuple[int, int, int, int],
            path_strings: list[str],
            autosize: bool,
            epsg: str
    ):
        super().__init__(bounding_box, path_strings, autosize)
        self.epsg = epsg

    @staticmethod
    def convert_s57_to_utm_shapefile(s57_file_path, shapefile_output_path, layer, epsg, bounding_box):
        x_min, y_min, x_max, y_max = map(str, bounding_box)
        ogr2ogr_cmd = [
            'ogr2ogr',
            '-f', 'ESRI Shapefile',     # Output format
            shapefile_output_path,      # Output shapefile
            s57_file_path,              # Input S57 file
            layer,
            '-t_srs', epsg.upper(),
            '-clipdst', x_min, y_min, x_max, y_max,
            '-skipfailures'
        ]
        try:
            subprocess.run(ogr2ogr_cmd, check=True)
            print(f"Conversion successful: {s57_file_path} -> {shapefile_output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e}")

    @staticmethod
    def convert_s57_depth_to_utm_shapefile(s57_file_path, shapefile_output_path, depth, epsg:str, bounding_box):
        x_min, y_min, x_max, y_max = map(str, bounding_box)
        ogr2ogr_cmd = [
            'ogr2ogr',
            '-f', 'ESRI Shapefile',     # Output format
            shapefile_output_path,      # Output shapefile
            s57_file_path,              # Input S57 file
            '-sql', 'SELECT * FROM DEPARE WHERE DRVAL1 >= ' + depth.__str__(),
            '-t_srs', epsg.upper(),
            '-clipdst', x_min, y_min, x_max, y_max,
            '-skipfailures'
        ]
        try:
            subprocess.run(ogr2ogr_cmd, check=True)
            print(f"Conversion successful: {s57_file_path} -> {shapefile_output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e}")

    def parse_resources(self, regions_list: list[Layer], resources: list[str], area: float) -> None:
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

        s57_path = None
        for path in self._file_paths:
            s57_path = self.get_s57_file(path)
        s57_path = r'' + s57_path.__str__()

        for region in regions_list:
            start_time = time.time()
            dest_path = r'' + self._shapefile_dir_path(region.label).__str__() + "\\" + region.label + ".shp"

            if isinstance(region, Seabed):
                self.convert_s57_depth_to_utm_shapefile(s57_path, dest_path, region.depth, self.epsg, self.bounding_box)
            elif isinstance(region, Land):
                self.convert_s57_to_utm_shapefile(s57_path, dest_path, "LNDARE", self.epsg, self.bounding_box)
            elif isinstance(region, Shore):
                self.convert_s57_to_utm_shapefile(s57_path, dest_path, "COALNE", self.epsg, self.bounding_box)

            records = list(self._read_shapefile(region.label))
            region.records_as_geometry(records)
            end_time = round(time.time() - start_time, 1)
            print(f"\rSaved {region.name} to shapefile in {end_time} s.")

    @staticmethod
    def get_s57_file(path) -> Path:
        for p in path.iterdir():
            if p.suffix == ".000":
                return p

    def _is_map_type(self, path):
        if path.is_dir():
            for p in path.iterdir():
                if p.suffix == ".000":
                    return True


