import subprocess
import time
from pathlib import Path

from seacharts.core import DataParser
from seacharts.layers import Layer, Land, Shore, Seabed
from seacharts.layers.layer import SingleDepthLayer


class S57Parser(DataParser):


    @staticmethod
    def convert_s57_to_shapefile(s57_file_path, shapefile_output_path, layer):
        ogr2ogr_cmd = [
            'ogr2ogr',
            '-f', 'ESRI Shapefile',  # Output format
            # '-update',
            '-t_srs', 'EPSG:32616',  # TODO fixit to take calculated utm zone
            shapefile_output_path,  # Output shapefile
            s57_file_path,  # Input S57 file
            layer,
            '-skipfailures'
        ]
        try:
            subprocess.run(ogr2ogr_cmd, check=True)
            print(f"Conversion successful: {s57_file_path} -> {shapefile_output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e}")

    @staticmethod
    def convert_s57_depth_to_shapefile(s57_file_path, shapefile_output_path, depth):
        ogr2ogr_cmd = [
            'ogr2ogr',
            '-f', 'ESRI Shapefile',  # Output format
            # '-update',
            '-t_srs', 'EPSG:32616',  # TODO fixit to take calculated utm zone
            shapefile_output_path,  # Output shapefile
            s57_file_path,  # Input S57 file
            '-sql', 'SELECT * FROM DEPARE WHERE DRVAL1 >= ' + depth.__str__(),
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

        # ogr2ogr was crashing for backslashes, temporary fix
        s57_path = None
        for path in self._file_paths:
            s57_path = self.get_s57_file(path)
        s57_path = s57_path.__str__().replace("\\", "/")
        # end

        for region in regions_list:
            if isinstance(region, Seabed):
                self.convert_s57_depth_to_shapefile(s57_path,
                                                    self._shapefile_dir_path(region.label).__str__() +
                                                    "\\" + region.label + ".shp",
                                                    region.depth)
            elif isinstance(region, Land):
                self.convert_s57_to_shapefile(s57_path,
                                              self._shapefile_dir_path(region.label).__str__() + "\\" +
                                              region.label + ".shp",
                                              "LNDARE")
            elif isinstance(region, Shore):
                self.convert_s57_to_shapefile(s57_path,
                                              self._shapefile_dir_path(region.label).__str__() + "\\" +
                                              region.label + ".shp",
                                              "LNDARE")

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


