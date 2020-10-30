from multiprocessing import Process
from typing import Optional

import seacharts.settings as config
from seacharts.display import Display


class ENC:
    """Class for parsing Navigational Electronic Chart data sets

    This class reads data sets issued by the Norwegian Mapping Authority
    (Kartverket) and extracts features from a user-specified region in
    Cartesian coordinates (easting/northing). Supports Shapely Points and
    Polygons ignoring all inner holes.

    :param origin: tuple(easting, northing) coordinates
    :param extent: tuple(width, height) of the area extent
    :param region: str or Sequence[str] of Norwegian regions
    :param depths: Sequence[int] of depth bins for features
    :param features: Sequence[str] of features to load or show
    :param new_data: bool indicating if new data should be parsed
    """

    def __init__(self,
                 *args: Optional,
                 new_data: Optional[bool] = False,
                 **kwargs: Optional):
        config.write_user_input_to_config_file(args, kwargs)
        self.scope = config.get_user_scope()
        self.environment = {f.__name__: f() for f in self.scope.features}
        self.load_environment_shapes(new_data)

    def __getitem__(self, item):
        return self.environment[item.capitalize()]

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
            feature.load(self.scope.bounding_box)

    def shapefiles_not_found(self):
        for feature in self.environment.keys():
            if not config.shapefile_exists(feature):
                print(f"ENC: Missing shapefile for feature layer "
                      f"'{feature.name}', initializing new parsing of "
                      f"downloaded ENC data")
                return True

    def process_external_data(self):
        print("ENC: Processing features from region...")
        for feature in self.environment.values():
            external_path = config.get_gdb_zip_paths(self.scope.region)
            feature.load(self.scope.bounding_box, external_path)
            feature.write_to_shapefile()
            print(f"  Feature layer extracted: {feature.name}")
        print("External data processing complete\n")

    def save_current_user_settings(self):
        pass

    @staticmethod
    def run_test_ship_simulation():
        Process(target=Display).start()
