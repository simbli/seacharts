from typing import Sequence, Union

from seacharts.display import Display
from seacharts.features import Seabed, Land, Shore, Ship
from seacharts.files import NorwegianCharts


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
    environment = {f.__name__.lower(): f() for f in (Seabed, Land, Shore)}
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
            self.region = region
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
        self.ships = [Ship()]
        self.load_environment_shapes(new_data)
        self.display = Display(self.ships, self.environment,
                               self.bounding_box, self.depths)

    def __getitem__(self, item):
        return self.environment[item]

    def __getattr__(self, item):
        return self.__getitem__(item)

    @property
    def supported_projection(self):
        return "EUREF89 UTM sone 33, 2d"

    @property
    def supported_environment(self):
        s = "Supported environment variables: "
        s += ', '.join(feature.lower() for feature in self.environment)
        return s + '\n'

    def load_environment_shapes(self, new_data):
        if self.shapefiles_not_found() or new_data:
            self.process_external_data()
        for feature in self.environment.values():
            feature.load(self.bounding_box)

    def shapefiles_not_found(self):
        for feature in self.environment.values():
            if not feature.shapefile.exists:
                print(f"ENC: Missing shapefile for feature layer "
                      f"'{feature.name}', initializing new parsing of "
                      f"downloaded ENC data")
                return True

    def process_external_data(self):
        print("ENC: Processing features from region...")
        fgdb = NorwegianCharts(self.region)
        for feature in self.environment.values():
            feature.load(self.bounding_box, fgdb)
            feature.write_to_shapefile()
            print(f"  Feature layer extracted: {feature.name}")
        print("External data processing complete\n")

    def simulate_test_ship(self):
        print("Simulating test ship...")
        for j in range(100):
            self.display.pause()
            for ship in self.ships:
                ship.update_position(self.display.fps)
            self.display.update(self.ships)
            self.display.save_frame(j)
        self.display.close()
        self.display.save_simulation()

    def show(self):
        self.display.show()
