from typing import Sequence, Union

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
    :param features: Sequence of supported features to be extracted
    :param depths: Sequence of integer depth bins for features
    :param new_data: bool indicating if new data should be parsed
    """
    default_origin = (38100, 6948700)
    default_window_size = (20000, 16000)
    default_region = 'Møre og Romsdal'

    def __init__(self,
                 origin: tuple = default_origin,
                 window_size: tuple = default_window_size,
                 region: Union[str, Sequence] = default_region,
                 features: Sequence = None,
                 depths: Sequence = None,
                 new_data: bool = False):

        self.parser = Parser(origin, window_size, region, features, depths)
        self.parser.update_charts_data(new_data)

    def read_feature_coordinates(self, feature):
        """Reads and returns the regional depths and coordinates of a feature

        :param feature: str or Feature object
        :return: [(depth, polygon_points), ...] if features are polygons
                     or [(depth, point_tuple), ...] if features are points
        """
        return self.parser.extract_coordinates(feature)

    def read_feature_shapes(self, feature):
        """Reads and returns the regional shapes of a feature

        :param feature: str or Feature object
        :return: list of Area or Position objects
        """
        return self.parser.extract_shapes(feature)
