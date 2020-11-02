import glob
from multiprocessing import Process
from typing import Optional

from PIL import Image

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
        self.environment = self.scope.environment
        self.load_environment_shapes(new_data)

    def __getattr__(self, item):
        return self.environment.__getattr__(item)

    @property
    def supported_projection(self):
        return "EUREF89 UTM sone 33, 2d"

    @property
    def supported_environment(self):
        s = "Supported environment variables: "
        s += ', '.join(config.supported_environment)
        return s + '\n'

    def load_environment_shapes(self, new_data):
        if self.shapefiles_not_found() or new_data:
            self.process_external_data()
        for feature in self.environment:
            feature.load(self.scope.bounding_box)

    def shapefiles_not_found(self):
        for feature in self.environment:
            if not config.shapefile_exists(feature.name):
                print(f"ENC: Missing shapefile for feature layer "
                      f"'{feature.name}', initializing new parsing of "
                      f"downloaded ENC data")
                return True

    def process_external_data(self):
        print("ENC: Processing features from region...")
        for feature in self.environment:
            external_path = config.get_gdb_zip_paths(self.scope.region)
            feature.load(self.scope.bounding_box, external_path)
            feature.write_to_shapefile()
            print(f"  Feature layer extracted: {feature.name}")
        print("External data processing complete\n")

    @staticmethod
    def visualize_environment():
        Process(target=Display).start()

    @staticmethod
    def save_simulation():
        print("Creating simulation GIF...")
        fp_in, fp_out = config.path_frame_files, config.path_simulation
        frame1, *frames = [Image.open(f) for f in glob.glob(fp_in)]
        frame1.save(fp=fp_out, format='GIF', append_images=frames,
                    save_all=True, duration=1000 / config.fps, loop=0)
        print(f"Done.")
