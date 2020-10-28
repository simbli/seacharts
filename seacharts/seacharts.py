from typing import Sequence, Union

from seacharts.display import Map
from seacharts.features import *
from seacharts.files import FileGDB, Shapefile


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
        if isinstance(region, str) or isinstance(region, Sequence):
            self.region = FileGDB(region)
        else:
            raise TypeError(
                f"ENC: Invalid region format for '{region}', should be "
                f"string or sequence of strings"
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
        self.bounding_box = *self.origin, *tr_corner
        self.update_charts_data(new_data)
        self.shapefiles = ()
        self.features = {}
        for feature in self.topography:
            key = feature.__name__.lower()
            self.features[key] = self.load(feature)
        self.ship = Ship(Ship.default_position)
        self.map = Map(self.bounding_box, self.depths)

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

    def update_charts_data(self, new_data):
        self.shapefiles = tuple(Shapefile(f) for f in self.topography)
        if not new_data:
            for shapefile in self.shapefiles:
                if not shapefile.exists:
                    print(f"ENC: Missing shapefile for feature layer "
                          f"'{shapefile.name}', initializing new parsing of "
                          f"downloaded ENC data")
                    new_data = True
                    break
        if new_data:
            self.process_external_data()

    def process_external_data(self):
        print("ENC: Processing features from region...")
        for shapefile in self.shapefiles:
            layer_name = shapefile.feature.layer_label
            records = self.region.read_files(layer_name, self.bounding_box)
            data = list(shapefile.select_data(r, True) for r in records)
            shapefile.write_data(data)
            print(f"  Feature layer extracted: {shapefile.name}")
        print("External data processing complete\n")

    def load(self, feature):
        data = tuple(Shapefile(feature).read(self.bounding_box))
        if len(data) == 0:
            raise ValueError(
                f"ENC: Feature layer {feature.__name__} returned no "
                f"shapes within bounding box {self.bounding_box}"
            )
        return [feature(shape, depth) for depth, shape in data]
