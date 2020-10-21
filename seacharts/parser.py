from typing import Sequence

from seacharts.feature import Feature
from seacharts.shapes import Area, Position


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

    default_depths = (0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500)
    supported_projection = 'EUREF89 UTM sone 33, 2d'
    supported_geometry = ('Polygon', 'Point')

    def __init__(self, origin, window_size, region, features, depths):
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
        elif not isinstance(features, str) and isinstance(depths, Sequence):
            self.depths = tuple(int(i) for i in depths)
        else:
            raise TypeError(
                "ENC: Depth bins should be a sequence of numbers"
            )
        if features is None:
            self.features = Feature.all_supported_features(region)
        elif isinstance(features, Sequence):
            if all(isinstance(f, Feature) for f in features):
                self.features = list(features)
            else:
                self.features = list(Feature(f, region) for f in features)
        else:
            raise TypeError(
                "ENC: Features should be a sequence of strings"
            )
        tr_corner = (i + j for i, j in zip(self.origin, self.window_size))
        self.bounding_box = *self.origin, *tr_corner

    def process_external_data(self):
        """Opens a regional FGDB file and writes reduced data to shapefiles

        This method must be called at least once before any of the read methods
        read_feature_coordinates   or   read_feature_shapes   in order to
        create the necessary shapefiles from which the simplified coordinates
        and depth data is read.

        :return: None
        """
        print("ENC: Processing features from region...")
        for feature in self.features:
            layer = list(feature.load_all_regional_shapes(self.bounding_box))
            feature.write_data_to_shapefile(layer)
            print(f"  Feature layer extracted: {feature.name}")
        print("External data processing complete\n")

    def read_feature_coordinates(self, feature):
        """Reads and returns the regional depths and coordinates of a feature

        :param feature: str or Feature object
        :return: [(depth, polygon_points), ...] if features are polygons
                     or [(depth, point_tuple), ...] if features are points
        """
        if not isinstance(feature, Feature):
            feature = self.get_feature_by_name(feature)
        layer = list(feature.read_shapefile(self.bounding_box))
        if len(layer) == 0:
            raise ValueError(
                f"ENC: Feature {feature.name} returned no shapes within"
                f"bounding box {self.bounding_box}"
            )
        return layer

    def read_feature_shapes(self, feature):
        """Reads and returns the regional shapes of a feature

        :param feature: str or Feature object
        :return: list of Area or Position objects
        """
        layer = self.read_feature_coordinates(feature)
        if isinstance(layer[0][1], tuple):
            return [Position(point, depth) for depth, point in layer]
        else:
            return [Area(points, depth) for depth, points in layer]

    def get_feature_by_name(self, name):
        feature = next((f for f in self.features if f.name == name), None)
        if not feature:
            raise ValueError(
                f"ENC: Feature '{name}' not found in feature list "
                f"{list(f.name for f in self.features)}"
            )
        return feature

    def update_charts_data(self, new_data):
        if not new_data:
            for feature in self.features:
                if not feature.shapefile_exists:
                    print(f"ENC: Missing shapefile for feature "
                          f"'{feature.name}', initializing new parsing of "
                          f"downloaded ENC data")
                    new_data = True
                    break
        if new_data:
            self.process_external_data()
