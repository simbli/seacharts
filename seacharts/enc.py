from pathlib import Path
from typing import Any, List, Tuple, Union

import matplotlib
from cartopy.crs import UTM

import seacharts.display as dis
import seacharts.environment as env
import seacharts.utils as utils


class ENC:
    """Electronic Navigational Charts

    Reads and extracts features from a user-specified region of spatial data
    given in Cartesian coordinates. Based on Matplotlib, Shapely and Cartopy.
    An independent visualization window may be spawned and displayed using the
    multiprocessing option. Geometric shapes may be accessed through the
    attributes 'land', 'shore', and 'seabed'.

    :param config_file: string containing path to configuration file
    :param multiprocessing: bool for independent visualization display
    :param kwargs: Includes the following optional parameters:
        :param size: tuple(width, height) of bounding box size
        :param origin: tuple(easting, northing) box origin of coordinates
        :param center: tuple(easting, northing) box center of coordinates
        :param buffer: int of dilation or erosion distance for geometries
        :param tolerance: int of maximum tolerance distance for geometries
        :param layers: list(str...) of feature layers to load or show
        :param depths: list(int...) of depth bins for feature layers
        :param files: list(str...) of file names for zipped FGDB files
        :param new_data: bool indicating if new files should be parsed
        :param border: bool for showing a border around the environment plot
        :param verbose: bool for status printing during geometry processing
    """

    def __init__(
        self,
        config_file: Path = utils.paths.config,
        multiprocessing=False,
        **kwargs
    ):
        self._setup_matplotlib_parameters()
        if multiprocessing:
            dis.Display.init_multiprocessing()
            return

        self._cfg = utils.config.ENCConfig(config_file, **kwargs)

        self._environment = env.Environment(self._cfg.settings)
        self.land = self._environment.topography.land
        self.shore = self._environment.topography.shore
        self.seabed = self._environment.hydrography.bathymetry
        self._display = dis.Display(self._cfg.settings, self._environment)

    @property
    def size(self) -> Tuple[int, int]:
        """
        :return: tuple of bounding box size
        """
        return self._environment.scope.extent.size

    @property
    def center(self) -> Tuple[int, int]:
        """
        :return: tuple of ENC center coordinates
        """
        return self._environment.scope.extent.center

    @property
    def origin(self) -> Tuple[int, int]:
        """
        :return: tuple of ENC origin (lower left) coordinates.
        """
        return self._environment.scope.extent.origin

    @property
    def bbox(self) -> Tuple[int, int, int, int]:
        """
        :return: tuple of bounding box coordinates (xmin, ymin, xmax, ymax)
        """
        return self._environment.scope.extent.bbox

    @property
    def considered_depths(self) -> List[int]:
        """
        :return: list of considered depth bins
        """
        return self._environment.scope.depths

    @property
    def utm_zone(self) -> int:
        """
        :return: integer of UTM zone number
        """
        return self._environment.scope.extent.utm_zone

    @property
    def figure_active(self) -> bool:
        """
        :return: boolean indicating if a figure is active
        """
        return self._display.is_active

    @property
    def crs(self) -> UTM:
        """Return the coordinate reference system projection used, as UTM object."""
        if self._display.crs is None:
            return UTM(self.utm_zone)
        return self._display.crs

    @property
    def supported_crs(self) -> str:
        """Return the supported coordinate reference system, as string."""
        return self._environment.supported_crs

    @property
    def supported_layers(self) -> str:
        """Return the supported feature layers."""
        return self._environment.supported_layers

    def fullscreen_mode(self, arg: bool = True) -> None:
        """
        Enable or disable fullscreen mode view of environment figure.
        :param arg: boolean switching fullscreen mode on or off
        :return: None
        """
        self._display.toggle_fullscreen(arg)

    def colorbar(self, arg: bool = True) -> None:
        """
        Enable or disable the colorbar legend of environment figure.
        :param arg: boolean switching the colorbar on or off.
        """
        self._display.toggle_colorbar(arg)

    def dark_mode(self, arg: bool = True) -> None:
        """
        Enable or disable dark mode view of environment figure.
        :param arg: boolean switching dark mode on or off
        :return: None
        """
        self._display.toggle_dark_mode(arg)

    def add_vessels(self, *args: Tuple[int, int, int, int, str]) -> None:
        """
        Add colored vessel features to the displayed environment plot.
        :param args: tuples with id, easting, northing, heading, color
        :return: None
        """
        self._display.refresh_vessels(list(args))

    def clear_vessels(self) -> None:
        """
        Remove all vessel features from the environment plot.
        :return: None
        """
        self._display.refresh_vessels([])

    def add_ownship(
        self,
        easting: int,
        northing: int,
        heading: float,
        hull_scale: float = 1.0,
        lon_scale: float = 10.0,
        lat_scale: float = 10.0,
    ) -> None:
        """
        Add the body of a controllable vessel to the environment.
        :param easting: int denoting the ownship X coordinate
        :param northing: int denoting the ownship Y coordinate
        :param heading: float denoting the ownship heading in degrees
        :param hull_scale: optional float scaling the ownship body size
        :param lon_scale: optional float scaling the longitudinal horizon
        :param lat_scale: optional float scaling the lateral horizon
        :return: None
        """
        self._environment.create_ownship(
            easting, northing, heading, hull_scale, lon_scale, lat_scale
        )
        self._display.update_plot()

    def remove_ownship(self) -> None:
        """
        Remove the controllable vessel from the environment.
        :return: None
        """
        self._environment.ownship = None

    def add_hazards(self, depth: int, buffer: int = 0) -> None:
        """
        Add hazardous areas to the environment, filtered by given depth.
        :param depth: int denoting the filter depth
        :param buffer: optional int denoting the buffer distance
        :return: None
        """
        self._environment.filter_hazardous_areas(depth, buffer)

    def draw_arrow(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str,
        width: float = None,
        fill: bool = False,
        head_size: float = None,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
    ) -> None:
        """
        Add a straight arrow overlay to the environment plot.
        :param start: tuple of start point coordinate pair
        :param end: tuple of end point coordinate pair
        :param color: str of line color
        :param width: float denoting the line buffer width
        :param fill: bool which toggles the interior arrow color on/off
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param head_size: float of head size (length) in meters
        :return: None
        """
        self._display.features.add_arrow(
            start, end, color, width, fill, head_size, thickness, edge_style
        )

    def draw_circle(
        self,
        center: Tuple[float, float],
        radius: float,
        color: str,
        fill: bool = True,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
        alpha: float = 1.0,
    ) -> None:
        """
        Add a circle or disk overlay to the environment plot.
        :param center: tuple of circle center coordinates
        :param radius: float of circle radius
        :param color: str of circle color
        :param fill: bool which toggles the interior disk color
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param alpha: float denoting the Matplotlib alpha value
        :return: None
        """
        self._display.features.add_circle(
            center, radius, color, fill, thickness, edge_style, alpha
        )

    def draw_line(
        self,
        points: List[Tuple[float, float]],
        color: str,
        width: float = None,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
        marker_type: str = None,
    ) -> None:
        """
        Add a straight line overlay to the environment plot.
        :param points: list of tuples of coordinate pairs
        :param color: str of line color
        :param width: float denoting the line buffer width
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param marker_type: str denoting the Matplotlib marker type
        :return: None
        """
        self._display.features.add_line(
            points, color, width, thickness, edge_style, marker_type
        )

    def draw_polygon(
        self,
        geometry: Union[Any, List[Tuple[float, float]]],
        color: str,
        interiors: List[List[Tuple[float, float]]] = None,
        fill: bool = True,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
        alpha: float = 1.0,
    ) -> None:
        """
        Add an arbitrary polygon shape overlay to the environment plot.
        :param geometry: Shapely geometry or list of exterior coordinates
        :param interiors: list of lists of interior polygon coordinates
        :param color: str of rectangle color
        :param fill: bool which toggles the interior shape color
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param alpha: float denoting the Matplotlib alpha value
        :return: None
        """
        self._display.features.add_polygon(
            geometry, color, interiors, fill, thickness, edge_style, alpha
        )

    def draw_rectangle(
        self,
        center: Tuple[float, float],
        size: Tuple[float, float],
        color: str,
        rotation: float = 0.0,
        fill: bool = True,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
        alpha: float = 1.0,
    ) -> None:
        """
        Add a rectangle or box overlay to the environment plot.
        :param center: tuple of rectangle center coordinates
        :param size: tuple of rectangle (width, height)
        :param color: str of rectangle color
        :param rotation: float denoting the rectangle rotation in degrees
        :param fill: bool which toggles the interior rectangle color
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param alpha: float denoting the Matplotlib alpha value
        :return: None
        """
        self._display.features.add_rectangle(
            center, size, color, rotation, fill, thickness, edge_style, alpha
        )

    def start_display(self) -> None:
        """
        Start the ENC figure display.
        :return: None
        """
        self._display.start(self._cfg.settings)

    def show_display(self, duration: float = 0.0) -> None:
        """
        Show a Matplotlib display window of a maritime environment.
        :param duration: optional int for window pause duration
        :return: None
        """
        self._display.show(duration)

    def get_display_handle(self):
        """Returns figure and axes handles to the seacharts display."""
        return self._display.figure, self._display.axes

    def refresh_display(self) -> None:
        """
        Manually redraw the environment display window.
        :return: None
        """
        self._display.draw_plot()

    def close_display(self) -> None:
        """
        Close the environment display window and clear all vessels.
        :return: None
        """
        self._display.terminate()
        self.clear_vessels()

    def save_image(
        self,
        name: str = None,
        path: Path | None = None,
        scale: float = 1.0,
        extension: str = "png",
    ) -> None:
        """
        Save the environment plot as a .png image.
        :param name: optional str of file name
        :param path: optional Path of file path
        :param scale: optional float scaling the image resolution
        :param extension: optional str of file extension name
        :return: None
        """
        self._display.save_figure(name, path, scale, extension)

    @staticmethod
    def _setup_matplotlib_parameters() -> None:
        """
        Set matplotlib parameters used for the entire ENC package.
        :return: None
        """
        matplotlib.rcParams["pdf.fonttype"] = 42
        matplotlib.rcParams["ps.fonttype"] = 42
        matplotlib.use("TkAgg")
