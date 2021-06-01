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

    def add_vessels(self, *args: Tuple[int, int, int, int, str]) -> None:
        """Add colored vessel features to the displayed environment plot."""
        self._display.update_vessels(list(args))

    def clear_vessels(self) -> None:
        """Remove all vessel features from the environment plot."""
        self._display.update_vessels([])

    def show_display(self, duration: int = None) -> None:
        """Show a Matplotlib display window of a maritime environment."""
        self._display.show(duration)

    def close_display(self) -> None:
        """Close the environment display window and clear all vessels."""
        self._display.terminate()
        self.clear_vessels()

    def save_image(self, name=None):
        """Save the environment plot as a .png image."""
        self._display.save_figure(name)
