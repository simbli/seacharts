from typing import Sequence, Union

from .files import Parser
from .shapes import Area, Position


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
    supported_projection = 'EUREF89 UTM sone 33, 2d'

    def __init__(self,
                 origin: tuple = default_origin,
                 window_size: tuple = default_window_size,
                 region: Union[str, Sequence] = default_region,
                 features: Sequence = None,
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
        tr_corner = (i + j for i, j in zip(self.origin, self.window_size))
        bounding_box = *self.origin, *tr_corner
        self.parser = Parser(bounding_box, region, features, depths)
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
        data = self.parser.extract_coordinates(feature)
        if isinstance(data[0][1], tuple):
            return [Position(point, depth) for depth, point in data]
        else:
            return [Area(points, depth) for depth, points in data]
