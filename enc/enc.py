
from typing import Sequence, Union

from enc.feature import Feature
from enc.shapes import Area, Position

_default_depths = (0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500)
_supported_geometry = ('Polygon', 'Point')
supported_projection = 'EUREF89 UTM sone 33, 2d'


class Parser:
    """Class for parsing Navigational Electronic Chart data sets

    This class reads data sets issued by the Norwegian Mapping Authority
    (Kartverket) and extracts features from a user-specified region in
    Cartesian coordinates (easting/northing). Supports Shapely Points and
    Polygons ignoring all inner holes.

    :param origin: tuple(easting, northing) coordinates
    :param window_size: tuple(width, height) of the window size
    :param features: Sequence of supported features to be extracted
    :param region: str or Sequence[str] of Norwegian regions
    """

    def __init__(self, origin: tuple, window_size: tuple,
                 region: Union[str, Sequence],
                 features: Sequence = None,
                 depths: Sequence = None):
        if isinstance(origin, tuple) and len(origin) == 2:
            self.origin = tuple(float(i) for i in origin)
        else:
            raise OriginFormatError(
                "Origin should be a tuple of the form "
                "(easting, northing) in meters"
            )
        if isinstance(window_size, tuple) and len(window_size) == 2:
            self.window_size = tuple(float(i) for i in window_size)
        else:
            raise WindowSizeFormatError(
                "Window size should be a tuple of the form "
                "(horizontal_width, vertical_height) in meters"
            )
        if depths is None:
            self.depths = _default_depths
        elif not isinstance(features, str) and isinstance(depths, Sequence):
            self.depths = tuple(int(i) for i in depths)
        else:
            raise DepthBinsFormatError(
                f"Depth bins should be a sequence of numbers"
            )
        if features is None:
            self.features = Feature.all_supported_features(region)
        elif not isinstance(features, str) and isinstance(features, Sequence):
            self.features = tuple(Feature(f, region) for f in features)
        else:
            raise FeaturesFormatError(
                f"Features should be a sequence of strings"
            )

    def process_external_data(self):
        """Opens a regional FGDB file and writes reduced data to shapefiles

        This method must be called at least once before any of the read methods
        read_feature_coordinates   or   read_feature_shapes   in order to
        create the necessary shapefiles from which the simplified coordinates
        and depth data is read.

        :return: None
        """
        print("Processing features from region...")
        for feature in self.features:
            layer = list(feature.load_all_regional_shapes(self.bounding_box))
            feature.write_data_to_shapefile(layer)
            print(f"    Feature layer extracted: '{feature.name}'")
        print("External data processing complete.\n")

    def read_feature_coordinates(self, feature):
        """Reads and returns the regional depths and coordinates of a feature

        :param feature: str or Feature object
        :return: [(depth, polygon_points), ...] if features are polygons
                     or [(depth, point_tuple), ...] if features are points
        """
        if isinstance(feature, str) and Feature.is_supported(feature):
            feature = next((f for f in self.features if f.name == feature))
        if isinstance(feature, Feature):
            return list(feature.read_shapefile(self.bounding_box))
        else:
            raise FeaturesFormatError(
                f"Features should be a sequence of strings"
            )

    def read_feature_shapes(self, feature):
        """Reads and returns the regional shapes of a feature

        :param feature: str or Feature object
        :return: list of Area or Position objects
        """
        layer = self.read_feature_coordinates(feature)
        if len(layer) > 0:
            if isinstance(layer[0][1], tuple):
                return [Position(point, depth) for depth, point in layer]
            else:
                return [Area(points, depth) for depth, points in layer]
        else:
            return []

    @property
    def top_right_corner(self):
        return tuple(i + j for i, j in zip(self.origin, self.window_size))

    @property
    def bounding_box(self):
        return *self.origin, *self.top_right_corner


class OriginFormatError(TypeError):
    pass


class WindowSizeFormatError(TypeError):
    pass


class DepthBinsFormatError(TypeError):
    pass


class FeaturesFormatError(TypeError):
    pass
