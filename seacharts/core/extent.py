"""
Contains the Extent class for defining the span of spatial data.
"""
import math
from pyproj import Transformer, CRS
from pyproj import Proj, transform

#TODO size in extent for latlong needs  fixing
class Extent:
    def __init__(self, settings: dict):
        self.size = tuple(settings["enc"].get("size", (0, 0)))
        self.UTM_zone = settings["enc"].get("UTM_zone")
        if "origin" in settings["enc"]:
            self.origin = tuple(settings["enc"].get("origin", (0, 0)))
            self.center = self._center_from_origin()

        if "center" in settings["enc"]:
            self.center = tuple(settings["enc"].get("center", (0, 0)))
            self.origin = self._origin_from_center()

        if settings["enc"].get("FGDB_depths", []):
            self.bbox = self._bounding_box_from_origin_size()
        elif settings["enc"].get("S57_layers", []):
            self.bbox = self._bounding_box_from_origin_size_lat_long()
        self.area: int = self.size[0] * self.size[1]

    @staticmethod
    def convert_lat_lon_to_utm(latitude, longitude, zone):
        in_proj = Proj(init='epsg:4326')  # WGS84
        out_proj = Proj(init='epsg:326' + zone)

        utm_east, utm_north = transform(in_proj, out_proj, longitude, latitude)
        utm_east = math.ceil(utm_east)
        utm_north = math.ceil(utm_north)
        return utm_east, utm_north

    def _origin_from_center(self) -> tuple[int, int]:
        return (
            self.center[0] - self.size[0] / 2,
            self.center[1] - self.size[1] / 2,
        )

    def _center_from_origin(self) -> tuple[int, int]:
        return (
            self.origin[0] + self.size[0] / 2,
            self.origin[1] + self.size[1] / 2,
        )

    def _bounding_box_from_origin_size(self) -> tuple[int, int, int, int]:
        x_min, y_min = self.origin
        x_max, y_max = x_min + self.size[0], y_min + self.size[1]
        return x_min, y_min, x_max, y_max

    def _bounding_box_from_origin_size_lat_long(self) -> tuple[int, int, int, int]:
        x_min, y_min = self.origin
        x_max, y_max = x_min + self.size[0], y_min + self.size[1]
        zone = str(math.floor(self.center[0] / 6 + 31))
        self.UTM_zone = zone
        converted_x_min, converted_y_min = self.convert_lat_lon_to_utm(y_min, x_min, zone)
        converted_x_max, converted_y_max = self.convert_lat_lon_to_utm(y_max, x_max, zone)
        return converted_x_min, converted_y_min, converted_x_max, converted_y_max
