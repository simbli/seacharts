"""
Contains the Extent class for defining the spatial boundaries, projections, and coordinate
transformations needed to work with ENC spatial data.
"""
import math
import re

from pyproj import Transformer


class Extent:
    """
    Extent class defines the spatial area, origin, center, size, and coordinates transformations 
    for a specified spatial data region. It manages coordinate reference systems (CRS) and conversions 
    between geographic (latitude/longitude) and projected (UTM) coordinates.

    :param settings: Dictionary containing configuration settings for ENC extent.
    """
    def __init__(self, settings: dict):
        """
        Initializes the Extent object with given settings, setting properties such as size, 
        origin, center, and CRS based on configuration.

        :param settings: Dictionary of ENC configuration settings including size, origin, CRS,
                         and center of the extent.
        """

        # Set the size of the extent, defaulting to (0, 0) if not specified in settings
        self.size = tuple(settings["enc"].get("size", (0, 0)))
        crs: str = settings["enc"].get("crs")

        # Set origin and center based on settings; if origin is given, calculate center, and vice versa
        if "origin" in settings["enc"]:
            self.origin = tuple(settings["enc"].get("origin", (0, 0)))
            self.center = self._center_from_origin()
        elif "center" in settings["enc"]:
            self.center = tuple(settings["enc"].get("center", (0, 0)))
            self.origin = self._origin_from_center()

        if crs.__eq__("WGS84"):
            # If CRS is WGS84, convert latitude/longitude to UTM
            self.utm_zone = self.wgs2utm(self.center[0])
            self.southern_hemisphere = Extent._is_southern_hemisphere(center_east=self.center[1])
            self.out_proj = Extent._get_epsg_proj_code(self.utm_zone, self.southern_hemisphere)
            self.size = self._size_from_lat_long()
            # Convert origin from lat/lon to UTM, recalculate center in UTM coordinates
            self.origin = self.convert_lat_lon_to_utm(self.origin[1], self.origin[0])
            self.center = self.origin[0] + self.size[0] / 2, self.origin[1] + self.size[1] / 2
        elif re.match(r'^UTM\d{2}[NS]', crs):
            # For UTM CRS, extract zone and hemisphere, and set EPSG projection code accordingly
            crs = re.search(r'\d+[A-Z]', crs).group(0)
            # eg. UTM33N:
                # utm_zone = 33
                # crs_hemisphere_code = 'N'
            self.utm_zone = crs[0:2]
            crs_hemisphere_code = crs[2]
            self.southern_hemisphere = Extent._is_southern_hemisphere(crs_hemisphere_sym=crs_hemisphere_code)
            self.out_proj = Extent._get_epsg_proj_code(self.utm_zone, self.southern_hemisphere)
        
        # Calculate bounding box and area based on origin and size
        self.bbox = self._bounding_box_from_origin_size()
        self.area: int = self.size[0] * self.size[1]

    @staticmethod
    def _is_southern_hemisphere(center_east: int = None, crs_hemisphere_sym: str = None) -> bool:
        """
        Determines if the hemisphere is southern based on either 'center_east' (UTM) or
        'crs_hemisphere_sym' ('N' for Northern, 'S' for Southern hemisphere).

        :param center_east: Integer value for the center's easting coordinate; if negative, the
                            center is in the southern hemisphere.
        :param crs_hemisphere_sym: String, either 'N' or 'S', indicating the UTM CRS hemisphere.
        :return: Boolean indicating if the southern hemisphere is determined.
        :raises ValueError: If neither or both arguments are provided.
        """
        if (center_east is not None) == (crs_hemisphere_sym is not None):
            raise ValueError("Specify only one of 'center_east' or 'crs_hemisphere_sym'.")

        # Determine hemisphere based on the provided parameter
        if center_east is not None:
            return center_east < 0
        elif crs_hemisphere_sym is not None:
            return crs_hemisphere_sym == 'S'
        
    @staticmethod
    def __get_hemisphere_epsg_code(is_southern_hemisphere: bool) -> str:
        return '7' if is_southern_hemisphere is True else '6'
    
    @staticmethod
    def _get_epsg_proj_code(utm_zone: str, is_southern_hemisphere: bool) -> str:
        """
        Constructs the EPSG projection code for the given UTM zone and hemisphere.

        :param utm_zone: String representing UTM zone.
        :param is_southern_hemisphere: Boolean indicating if the zone is in the southern hemisphere.
        :return: EPSG code as a string.
        """
        hemisphere_code = Extent.__get_hemisphere_epsg_code(is_southern_hemisphere)
        return 'epsg:32' + hemisphere_code + utm_zone

    @staticmethod
    def wgs2utm(longitude):
        """
        Calculates the UTM zone based on the given longitude.

        :param longitude: Longitude in decimal degrees.
        :return: String representing the UTM zone number.
        """
        return str(math.floor(longitude / 6 + 31))

    def convert_lat_lon_to_utm(self, latitude, longitude):
        """
        Converts latitude and longitude coordinates to UTM coordinates.

        :param latitude: Latitude in decimal degrees.
        :param longitude: Longitude in decimal degrees.
        :return: Tuple of UTM east and north coordinates.
        """
        in_proj = 'epsg:4326'  # WGS84

        transformer = Transformer.from_crs(in_proj, self.out_proj, always_xy=True)
        utm_east, utm_north = transformer.transform(longitude, latitude)

        utm_east = math.ceil(utm_east)
        utm_north = math.ceil(utm_north)
        return utm_east, utm_north

    def convert_utm_to_lat_lon(self, utm_east, utm_north):
        """
        Converts UTM coordinates to latitude and longitude.

        :param utm_east: UTM easting coordinate.
        :param utm_north: UTM northing coordinate.
        :return: Tuple of latitude and longitude.
        """
        out_proj = 'epsg:4326'  # WGS84
        in_proj = self.out_proj
        transformer = Transformer.from_crs(in_proj, out_proj, always_xy=True)
        longitude, latitude = transformer.transform(utm_east, utm_north)

        return latitude, longitude

    def _origin_from_center(self) -> tuple[int, int]:
        """
        Calculates the origin coordinates based on the center and size.

        :return: Tuple of origin x and y coordinates.
        """
        return (
            int(self.center[0] - self.size[0] / 2),
            int(self.center[1] - self.size[1] / 2),
        )

    def _center_from_origin(self) -> tuple[int, int]:
        """
        Calculates the center coordinates based on the origin and size.

        :return: Tuple of center x and y coordinates.
        """
        return (
            int(self.origin[0] + self.size[0] / 2),
            int(self.origin[1] + self.size[1] / 2),
        )

    def _bounding_box_from_origin_size(self) -> tuple[int, int, int, int]:
        """
        Calculates the bounding box based on the origin and size.

        :return: Tuple of bounding box coordinates (x_min, y_min, x_max, y_max).
        """
        x_min, y_min = self.origin
        x_max, y_max = x_min + self.size[0], y_min + self.size[1]
        return x_min, y_min, x_max, y_max

    def _size_from_lat_long(self) -> tuple[int, int]:
        """
        Converts geographic size (latitude/longitude) to UTM size.

        :return: Tuple of width and height in UTM coordinates.
        """
        x_min, y_min = self.origin
        x_max, y_max = x_min + self.size[0], y_min + self.size[1]
        converted_x_min, converted_y_min = self.convert_lat_lon_to_utm(y_min, x_min)
        converted_x_max, converted_y_max = self.convert_lat_lon_to_utm(y_max, x_max)
        return converted_x_max - converted_x_min, converted_y_max - converted_y_min

    def _bounding_box_from_origin_size_lat_long(self) -> tuple[int, int, int, int]:
        """
        Calculates the bounding box in UTM coordinates based on origin and geographic size.

        :return: Tuple of bounding box coordinates (x_min, y_min, x_max, y_max) in UTM.
        """
        x_min, y_min = self.origin
        x_max, y_max = x_min + self.size[0], y_min + self.size[1]
        converted_x_min, converted_y_min = self.convert_lat_lon_to_utm(y_min, x_min)
        converted_x_max, converted_y_max = self.convert_lat_lon_to_utm(y_max, x_max)
        self.size = tuple([converted_x_max - converted_x_min, converted_y_max - converted_y_min])
        return converted_x_min, converted_y_min, converted_x_max, converted_y_max
