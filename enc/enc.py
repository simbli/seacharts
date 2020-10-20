
from typing import Sequence, Union

import fiona

from enc.feature import Feature, supported_features
from enc.region import Region
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

        if self._is_tuple_with_length_two(origin):
            self.origin = tuple(float(i) for i in origin)
        else:
            raise OriginFormatError(
                "Origin should be a tuple of the form "
                "(easting, northing) in meters"
            )
        if self._is_tuple_with_length_two(window_size):
            self.window_size = tuple(float(i) for i in window_size)
        else:
            raise SizeFormatError(
                "Window size should be a tuple of the form "
                "(horizontal_width, vertical_height) in meters"
            )
        if isinstance(region, str):
            self.region = (Region(region),)
        elif self._is_sequence_of_strings(region):
            self.region = tuple(Region(r) for r in region)
        else:
            raise RegionFormatError(
                f"Region '{region}' not valid, should be string or "
                f"sequence of strings"
            )
        if features is None:
            self.features = tuple(Feature(f) for f in supported_features)
        elif self._is_sequence_of_strings(features):
            self.features = tuple(Feature(f) for f in features)
        else:
            raise FeaturesFormatError(
                f"Features '{features}' not valid, should be "
                f"sequence of strings"
            )
        if depths is None:
            self.depths = _default_depths
        elif isinstance(depths, Sequence):
            self.depths = tuple(int(i) for i in depths)
        else:
            raise DepthBinsFormatError(
                f"Depth bins should be a sequence of numbers"
            )
        t_r_corner = (self.origin[i] + self.window_size[i] for i in range(2))
        self._bounding_box = *self.origin, *t_r_corner

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
            layer = self._load_all_regional_shapes(feature)
            feature.write_data_to_shapefile(layer)
            print(f"    Feature layer extracted: '{feature.name}'")
        print("External data processing complete.\n")

    def read_feature_coordinates(self, feature):
        """Reads and returns the regional depths and coordinates of a feature

        :param feature: str or Feature object
        :return: [(depth, polygon_points), ...] if features are polygons
                     or [(depth, point_tuple), ...] if features are points
        """
        if isinstance(feature, str):
            feature = Feature(feature)
        with feature.shapefile_reader as file:
            return list(self._parse_records(file, 'depth'))

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

    def _load_all_regional_shapes(self, feature):
        data = []
        for r in self.region:
            if feature.id in fiona.listlayers(r.zip_path):
                depth_label = feature.depth_label
                with feature.fgdb_reader(r) as file:
                    data += list(self._parse_records(file, depth_label))
        return data

    def _parse_records(self, file, depth_label):
        for record in file.filter(bbox=self._bounding_box):
            depth = record['properties'][depth_label] if depth_label else 0
            coords = record['geometry']["coordinates"]
            if file.schema['geometry'] == 'Point':
                shape = coords
            else:
                shape = coords[0]
            yield depth, shape

    @staticmethod
    def _is_tuple_with_length_two(o):
        return isinstance(o, tuple) and len(o) == 2

    @staticmethod
    def _is_sequence_of_strings(o):
        return isinstance(o, Sequence) and all(isinstance(s, str) for s in o)


class OriginFormatError(TypeError):
    pass


class SizeFormatError(TypeError):
    pass


class RegionFormatError(TypeError):
    pass


class FeaturesFormatError(TypeError):
    pass


class DepthBinsFormatError(TypeError):
    pass
