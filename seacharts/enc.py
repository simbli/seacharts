from pathlib import Path

from seacharts.display import Display
from seacharts.environment import Environment
from seacharts.spatial.base import Layer
from seacharts.utils.config import Config


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
        return self._environment.topography.land

    @property
    def shore(self) -> Layer:
        """
        :return: shore layer container of Shapely geometries
        """
        return self._environment.topography.shore

    @property
    def seabed(self) -> dict[int, Layer]:
        """
        :return: seabed dict of Shapely geometries for each depth bin
        """
        return self._environment.hydrography.bathymetry

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
