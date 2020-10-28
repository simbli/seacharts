from typing import Sequence, Union

from seacharts.display import Map
from seacharts.features import *
from seacharts.files import Parser


class ENC:
    """Class for parsing Navigational Electronic Chart data sets

    This class reads data sets issued by the Norwegian Mapping Authority
    (Kartverket) and extracts features from a user-specified region in
    Cartesian coordinates (easting/northing). Supports Shapely Points and
    Polygons ignoring all inner holes.

    :param origin: tuple(easting, northing) coordinates
    :param window_size: tuple(width, height) of the window size
    :param region: str or Sequence[str] of Norwegian regions
    :param depths: Sequence of integer depth bins for features
    :param new_data: bool indicating if new data should be parsed
    """
    topography = (Seabed, Land, Shore, Rocks, Shallows)
    default_depths = [0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500]
    default_window_size = (3000, 2000)
    default_origin = (42600, 6956400)
    default_region = 'Møre og Romsdal'

    def __init__(self,
                 origin: tuple = default_origin,
                 window_size: tuple = default_window_size,
                 region: Union[str, Sequence] = default_region,
                 depths: Sequence = None,
                 new_data: bool = False):

        if isinstance(origin, tuple) and len(origin) == 2:
            self.origin = origin
        else:
            raise TypeError(
                "ENC: Origin should be a tuple of size two"
            )
        if isinstance(window_size, tuple) and len(window_size) == 2:
            self.window_size = window_size
        else:
            raise TypeError(
                "ENC: Window size should be a tuple of size two"
            )
        if depths is None:
            self.depths = self.default_depths
        elif not isinstance(depths, str) and isinstance(depths, Sequence):
            self.depths = list(int(i) for i in depths)
        else:
            raise TypeError(
                "ENC: Depth bins should be a sequence of numbers"
            )
        tr_corner = (i + j for i, j in zip(self.origin, self.window_size))
        bounding_box = *self.origin, *tr_corner
        self.parser = Parser(bounding_box, region, self.depths)
        self.parser.update_charts_data(self.topography, new_data)
        self.features = {}
        for feature in self.topography:
            key = feature.__name__.lower()
            self.features[key] = self.parser.load(feature)
        self.ship = Ship(Ship.default_position)
        self.map = Map(bounding_box, self.depths)

    def __getitem__(self, item):
        return self.features[item]

    def __getattr__(self, item):
        return self.__getitem__(item)

    @property
    def supported_features(self):
        return tuple(f.__name__ for f in self.topography)

    @property
    def supported_projection(self):
        return "EUREF89 UTM sone 33, 2d"
