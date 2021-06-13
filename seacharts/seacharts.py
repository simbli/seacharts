from typing import List, Optional, Tuple

import seacharts.display as dis
import seacharts.environment as env


class ENC:
    """Electronic Navigational Charts

    Reads and extracts features from a user-specified region of spatial data
    given in Cartesian coordinates. Based on Matplotlib, Shapely and Cartopy.
    An independent visualization window may be spawned and displayed using the
    multiprocessing option. Geometric shapes may be accessed through the
    attributes 'land', 'shore', and 'seabed'.

    :param size: tuple(width, height) of bounding box size
    :param origin: tuple(easting, northing) box origin of coordinates
    :param center: tuple(easting, northing) box center of coordinates
    :param buffer: int of dilation or erosion distance for geometries
    :param tolerance: int of maximum tolerance distance for geometries
    :param layers: list(str...) of feature layers to load or show
    :param depths: list(int...) of depth bins for feature layers
    :param files: list(str...) of file names for zipped FGDB files
    :param new_data: bool indicating if new files should be parsed
    :param verbose: bool for status printing during geometry processing
    :param multiprocessing: bool for independent visualization display
    """

    def __init__(self,
                 size: Tuple[int, int] = None,
                 origin: Tuple[int, int] = None,
                 center: Tuple[int, int] = None,
                 buffer: Optional[int] = None,
                 tolerance: Optional[int] = None,
                 layers: Optional[List[str]] = None,
                 depths: Optional[List[int]] = None,
                 files: Optional[List[str]] = None,
                 new_data: Optional[bool] = None,
                 verbose: Optional[bool] = None,
                 multiprocessing: bool = False,
                 ):
        if multiprocessing:
            dis.Display.init_multiprocessing()
            return
        self._environment = env.Environment(
            size, origin, center, tolerance, buffer,
            layers, depths, files, new_data, verbose,
        )
        self.land = self._environment.topography.land
        self.shore = self._environment.topography.shore
        self.seabed = self._environment.hydrography.bathymetry
        self._display = dis.Display(self._environment)

    @property
    def supported_crs(self) -> str:
        """Return the supported coordinate reference system."""
        return self._environment.supported_crs

    @property
    def supported_layers(self) -> str:
        """Return the supported feature layers."""
        return self._environment.supported_layers

    def dark_mode(self, arg: bool = True):
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

    def add_ownship(self,
                    easting: int,
                    northing: int,
                    heading: float,
                    hull_scale: float = 1.0,
                    lon_scale: float = 10.0,
                    lat_scale: float = 10.0,
                    ):
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

    def remove_ownship(self):
        """
        Remove the controllable vessel from the environment.
        :return: None
        """
        self._environment.ownship = None

    def add_hazards(self, depth: int, buffer: int = 0) -> None:
        """
        Add hazardous areas the environment, filtered by given depth.
        :param depth: int denoting the filter depth
        :param buffer: optional int denoting the buffer distance
        :return: None
        """
        self._environment.filter_hazardous_areas(depth, buffer)

    def show_display(self, duration: int = 0.0) -> None:
        """
        Show a Matplotlib display window of a maritime environment.
        :param duration: optional int for window pause duration
        :return: None
        """
        self._display.show(duration)

    def close_display(self) -> None:
        """
        Close the environment display window and clear all vessels.
        :return: None
        """
        self._display.terminate()
        self.clear_vessels()

    def save_image(self, name: str = None, scale: float = 1.0):
        """
        Save the environment plot as a .png image.
        :param name: optional str of file name
        :param scale: optional float scaling the image resolution
        :return: None
        """
        self._display.save_figure(name, scale)
