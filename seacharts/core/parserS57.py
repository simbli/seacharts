import subprocess
import time
from seacharts.core import DataParser
from seacharts.layers import Layer


class S57Parser(DataParser):
    @staticmethod
    def convert_s57_to_shapefile(s57_file_path, shapefile_output_path, parsedLayers):
        commandLayers = ""
        for layer in parsedLayers:
            commandLayers += layer + " "
        commandLayers = commandLayers.split(' ')
        for layer in commandLayers:
            layer = layer.replace(" ", "")
            if len(layer) > 0:
                ogr2ogr_cmd = [
                    'ogr2ogr',
                    '-f', 'ESRI Shapefile',  # Output format
                    # '-update',
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
        print(f"Processing {area // 10 ** 6} km^2 of ENC features:")  # TODO: return when fixing coords
        for regions in regions_list:
            #TODO: for each region,
            # generate appropriate destination path with shapefile_path() func
            # get source S-57 path from file_paths() func

            # start_time = time.time()
            # records = self._load_from_file(regions)
            # info = f"{len(records)} {regions.name} geometries"

    def _is_map_type(self, path):
        if path.is_dir():
            for p in path.iterdir():
                if p.suffix == ".000":
                    return True
