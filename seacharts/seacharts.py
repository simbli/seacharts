import csv
import glob
from multiprocessing import Process
from typing import Optional

from PIL import Image

from . import settings as config
from .display import Display


class ENC:
    """Class for parsing Electronic Navigational Chart data sets

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
        if item in self.environment.__dict__:
            return getattr(self.environment, item)
        elif item in self.__dict__:
            return getattr(self, item)
        else:
            raise AttributeError(item)

    @property
    def supported_projection(self):
        return f"EUREF89 UTM sone 33, 2d"

    @property
    def supported_environment(self):
        s = f"Supported environment variables: "
        s += f', '.join(config.supported_environment)
        return s + '\n'

    def load_environment_shapes(self, new_data):
        if self.shapefiles_not_found() or new_data:
            self.process_external_data()
        for feature in self.environment:
            feature.load(self.scope.bounding_box)

    def shapefiles_not_found(self):
        for feature in self.environment:
            if not feature.shapefile_exists:
                print(f"ENC: Missing shapefile for feature layer "
                      f"'{feature.name}', initializing new parsing of "
                      f"downloaded ENC data")
                return True

    def process_external_data(self):
        print(f"ENC: Processing features from region...")
        for feature in self.environment:
            external_path = config.get_gdb_zip_paths(self.scope.region)
            feature.load(self.scope.bounding_box, external_path)
            feature.write_to_shapefile()
            print(f"  Feature layer extracted: {feature.name}")
        print(f"External data processing complete\n")

    @staticmethod
    def visualize_environment():
        Process(target=Display).start()

    @staticmethod
    def save_visualization():
        print("Creating simulation GIF...")
        fp_in, fp_out = config.path_frame_files, config.path_simulation
        frame1, *frames = [Image.open(f) for f in glob.glob(str(fp_in))]
        frame1.save(fp=str(fp_out), format='GIF', append_images=frames,
                    save_all=True, duration=1000 / config.fps, loop=0)
        print(f"Done.")

    @staticmethod
    def write_ships_to_csv(poses):
        lines = [('x_position', 'y_position', 'heading')]
        for pose in poses:
            lines.append(pose)
        with open(config.path_ships, 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            writer.writerows(lines)
