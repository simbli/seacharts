"""
Contains the ENC class for reading, storing and plotting maritime spatial data.
"""
import _warnings
from pathlib import Path
from shapely.geometry import Point, Polygon
from seacharts.core import Config
from seacharts.display import Display
from seacharts.environment import Environment
from seacharts.environment.weather import WeatherData
from seacharts.layers import Layer

class ENC:
    """
    Electronic Navigational Charts

    Reads and extracts features from a user-specified region of spatial data,
    based on Matplotlib and Shapely. Geometric shapes may be accessed through
    the attributes 'land', 'shore', and 'seabed', and 'display' may be used to
    visualize the data and marine vessels in a dynamic user interface.

    :param config: Config object or a valid path to a .yaml config file
    """

    def __init__(self, config: Config | Path | str = None):
        self._config = config if isinstance(config, Config) else Config(config)
        self._environment = Environment(self._config.settings)
        self._display = None

    def get_depth_at_coord(self, easting: int, northing: int) -> int:
        """
        Retrieves the seabed depth at a given coordinate.

        :param easting: The easting (x-coordinate) in the coordinate system used by ENC.
        :param northing: The northing (y-coordinate) in the coordinate system used by ENC.
        :return: Depth as an integer if the point is within a seabed polygon, else None.
        """
        point = Point(easting, northing)
        for seabed in reversed(self.seabed.values()):
            if any(polygon.contains(point) for polygon in seabed.geometry.geoms):
                return seabed.depth
        return None
    
    def is_coord_in_layer(self, easting: int, northing: int, layer_name: str):
        """
        Checks if a coordinate is within a specified layer.

        :param easting: The easting (x-coordinate) in the coordinate system used by ENC.
        :param northing: The northing (y-coordinate) in the coordinate system used by ENC.
        :param layer_name: The name of the layer to check, as a string.
        :return: True if the coordinate is in the specified layer; False if not. Returns None if no matching layer was found.
        """
        layer = self._environment.get_layer_by_name(layer_name)
        point = Point(easting, northing)
        if layer is not None:
            if any(polygon.contains(point) for polygon in layer.geometry.geoms):
                return True
        return False
    
    def get_param_value_at_coords(self, easting: int, northing: int, layer_name: str, param_name: str):
        param_name = param_name.upper()
        if self.is_coord_in_layer(easting, northing, layer_name):
            layer: Layer = self._environment.get_layer_by_name(layer_name)
            parameters: dict | None = layer.get_params_at_coord(easting, northing)
            if parameters is not None:
                return parameters[param_name]
            _warnings.warn(f"Couldn't find any value for parameter {param_name} in layer {layer_name}")
        return None

    def update(self) -> None:
        """
        Update ENC with spatial data parsed from user-specified resources
        :return: None
        """
        self._environment.map.parse_resources_into_shapefiles()

    @property
    def display(self) -> Display:
        """
        :return: display to visualize maritime geometric data and vessels
        """
        if self._display is None:
            self._display = Display(self._config.settings, self._environment)
        return self._display

    @property
    def land(self) -> Layer:
        """
        :return: land layer container of Shapely geometries
        """
        return self._environment.map.land

    @property
    def shore(self) -> Layer:
        """
        :return: shore layer container of Shapely geometries
        """
        return self._environment.map.shore

    @property
    def seabed(self) -> dict[int, Layer]:
        """
        :return: seabed dict of Shapely geometries for each depth bin
        """
        return self._environment.map.bathymetry

    @property
    def size(self) -> tuple[int, int]:
        """
        :return: tuple of ENC bounding box size
        """
        return self._environment.scope.extent.size

    @property
    def origin(self) -> tuple[int, int]:
        """
        :return: tuple of ENC origin (lower left) coordinates.
        """
        return self._environment.scope.extent.origin

    @property
    def center(self) -> tuple[int, int]:
        """
        :return: tuple of ENC center coordinates
        """
        return self._environment.scope.extent.center

    @property
    def bbox(self) -> tuple[int, int, int, int]:
        """
        :return: tuple of bounding box coordinates (x_min, y_min, x_max, y_max)
        """
        return self._environment.scope.extent.bbox

    @property
    def depth_bins(self) -> list[int]:
        """
        :return: list of considered depth bins
        """
        return self._environment.scope.depths

    @property
    def weather_names(self) -> list[str]:
        """
        :return: #TODO
        """
        return self._environment.weather.weather_names

    @property
    def weather_data(self) -> WeatherData:
        """
        :return: #TODO
        """
        return self._environment.weather
