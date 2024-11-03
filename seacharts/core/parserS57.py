import os.path
import subprocess
import time
from pathlib import Path

from seacharts.core import DataParser
from seacharts.layers import Layer, Land, Shore, Seabed


class S57Parser(DataParser):
    """
    Parser for S57 maritime spatial data. This class manages data parsing, 
    conversion to shapefiles, and filtering by depth using a specified bounding box 
    and EPSG code for the coordinate reference system.

    :param bounding_box: Tuple defining bounding box coordinates as (xmin, ymin, xmax, ymax).
    :param path_strings: List of paths to data sources.
    :param epsg: EPSG code for the desired coordinate reference system.
    """
    def __init__(
            self,
            bounding_box: tuple[int, int, int, int],
            path_strings: list[str],
            epsg: str
    ):
        super().__init__(bounding_box, path_strings)
        self.epsg = epsg

    def get_source_root_name(self) -> str:
        """ 
        Returns the stem (base filename without suffix) of the first valid S57 file 
        path in the given data paths.

        :return: The stem of the first valid S57 file.
        """
        for path in self._file_paths:
            path = self.get_s57_file_path(path)
            if path is not None:
                return path.stem

    @staticmethod
    def __run_org2ogr(ogr2ogr_cmd, s57_file_path, shapefile_output_path) -> None:
        """
        Executes the ogr2ogr command to convert S57 files to shapefiles.

        :param ogr2ogr_cmd: Command to be executed for conversion.
        :param s57_file_path: Path to the input S57 file.
        :param shapefile_output_path: Path where the output shapefile will be saved.
        """
        try:
            subprocess.run(ogr2ogr_cmd, check=True)
            print(f"Conversion successful: {s57_file_path} -> {shapefile_output_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error during conversion: {e}")

    @staticmethod
    def convert_s57_to_utm_shapefile(s57_file_path, shapefile_output_path, layer: str, epsg:str, bounding_box):
        """
        Converts a given layer from a S57 file to a UTM shapefile, clipping to the specified bounding box.

        :param s57_file_path: Path to the input S57 file.
        :param shapefile_output_path: Path where the output shapefile will be saved.
        :param layer: Layer type to be extracted (e.g., "LNDARE").
        :param epsg: EPSG code for the desired coordinate reference system.
        :param bounding_box: Tuple defining bounding box coordinates as (xmin, ymin, xmax, ymax).
        """
        x_min, y_min, x_max, y_max = map(str, bounding_box)
        ogr2ogr_cmd = [
            'ogr2ogr',
            '-f', 'ESRI Shapefile',                 # Output format
            shapefile_output_path,                  # Output shapefile
            s57_file_path,                          # Input S57 file
            layer,                                  # Converted layer name
            '-t_srs', epsg.upper(),                 # Target spatial reference system
            '-clipdst', x_min, y_min, x_max, y_max, # Clipping to bounding box
            '-skipfailures'                         # Skip failures in processing
        ]
        S57Parser.__run_org2ogr(ogr2ogr_cmd, s57_file_path, shapefile_output_path)
        

    @staticmethod
    def convert_s57_depth_to_utm_shapefile(s57_file_path, shapefile_output_path, depth, epsg:str, bounding_box, next_depth = None):
        """
        Converts a S57 file DEPARE layer to a UTM shapefile based on specified depth criteria.

        :param s57_file_path: Path to the input S57 file.
        :param shapefile_output_path: Path where the output shapefile will be saved.
        :param depth: Minimum depth for filtering the data.
        :param epsg: EPSG code for the desired coordinate reference system.
        :param bounding_box: Tuple defining bounding box coordinates as (xmin, ymin, xmax, ymax).
        :param next_depth: Optional; maximum depth for filtering the data.
        """
        x_min, y_min, x_max, y_max = map(str, bounding_box)
        query = f'SELECT * FROM DEPARE WHERE DRVAL1 >= {depth.__str__()}'
        if next_depth is not None:
            query += f' AND DRVAL1 < {next_depth.__str__()}'
        ogr2ogr_cmd = [
            'ogr2ogr',
            '-f', 'ESRI Shapefile',                 # Output format
            shapefile_output_path,                  # Output shapefile
            s57_file_path,                          # Input S57 file
            '-sql', query,                          # SQL query for depth filtering
            '-t_srs', epsg.upper(),                 # Target spatial reference system
            '-clipdst', x_min, y_min, x_max, y_max, # Clipping to bounding box
            '-skipfailures'                         # Skip failures in processing
        ]
        S57Parser.__run_org2ogr(ogr2ogr_cmd, s57_file_path, shapefile_output_path)

    def parse_resources(
            self,
            regions_list: list[Layer],
            resources: list[str],
            area: float
    ) -> None:
        """
        Parses the provided resources for specified regions and processes them into shapefiles.

        :param regions_list: List of Layer objects representing different regions to be processed.
        :param resources: List of resource paths to be considered for processing.
        :param area: Area of the region being processed, used for validation.
        """
        if not self._valid_paths_and_resources(self.paths, resources, area): 
            return # interrupt parsing if paths are not valid
        s57_path = None
        for path in self._file_paths:
            s57_path = self.get_s57_file_path(path)
        s57_path = str(s57_path)

        # Separate Seabeds from rest of regions to extract depths from DEPARE correctly
        seabeds = [region for region in regions_list if isinstance(region, Seabed)]
        rest_of_regions = [region for region in regions_list if not isinstance(region, Seabed)]
        
        for index, region in enumerate(seabeds):
            self._parse_S57_depth(index, region, s57_path, seabeds)
        for region in rest_of_regions:
            self._parse_S57_region(region, s57_path)
        print(f"\rFinished processing {len(regions_list)} layers for S57 map at {s57_path}")

    def _parse_S57_region(self, region: Layer, s57_path: str):
        """
        Parses a region from the S57 file and converts it to a shapefile.

        :param region: Layer object representing the region to be parsed.
        :param s57_path: Path to the input S57 file.
        """
        start_time = time.time()
        dest_path = self.__get_dest_path(region.label)

        if isinstance(region, Land):
            self.convert_s57_to_utm_shapefile(s57_path, dest_path, "LNDARE", self.epsg, self.bounding_box)
        elif isinstance(region, Shore):
            self.convert_s57_to_utm_shapefile(s57_path, dest_path, "COALNE", self.epsg, self.bounding_box)
        else:
            self.convert_s57_to_utm_shapefile(s57_path, dest_path, region.name, self.epsg, self.bounding_box)

        self.load_shapefiles(region)
        end_time = round(time.time() - start_time, 1)
        print(f"\rSaved {region.name} to shapefile in {end_time} s.")

    def _parse_S57_depth(self, index: int, region: Seabed, s57_path: str, seabeds: list[Seabed]):
        """
        Parses a seabed region (DEPARE) from the S57 file and converts it to a shapefile based on depth.

        :param index: Index of the seabed region in the list.
        :param region: Seabed object representing the region to be parsed.
        :param s57_path: Path to the input S57 file.
        :param seabeds: List of all seabed regions.
        """
        start_time = time.time()
        dest_path = self.__get_dest_path(region.label)
        if index < len(seabeds) - 1:
            next_depth = seabeds[index + 1].depth
            self.convert_s57_depth_to_utm_shapefile(s57_path, dest_path, region.depth, self.epsg, self.bounding_box, next_depth)
        else:
            self.convert_s57_depth_to_utm_shapefile(s57_path, dest_path, region.depth, self.epsg, self.bounding_box)
        self.load_shapefiles(region)
        end_time = round(time.time() - start_time, 1)
        print(f"\rSaved {region.name} to shapefile in {end_time} s.")

    def __get_dest_path(self, region_label):
        """
        Generates the destination path for saving the shapefile based on the region label.

        :param region_label: Label of the region for which the shapefile path is being generated.
        :return: Path for the shapefile destination.
        """
        return os.path.join(self._shapefile_dir_path(region_label), region_label + ".shp")


    @staticmethod
    def get_s57_file_path(path: Path) -> Path | None:
        """
        Retrieves the path of the first S57 file (with .000 extension) in the given directory.

        :param path: Path to the directory to be searched.
        :return: Path to the found S57 file, or None if no valid file is found.
        """
        for p in path.iterdir():
            if p.suffix == ".000":
                return p
        return None

    def _is_map_type(self, path: Path) -> bool:
        """
        Determines if the specified path corresponds to a valid S57 map type (file or directory).

        :param path: Path to be checked.
        :return: True if the path is a valid map type, otherwise False.
        """
        if path.is_dir():
            for p in path.iterdir():
                if p.suffix == ".000":
                    return True
        elif path.is_file():
            if path.suffix == ".000":
                    return True
        return False



