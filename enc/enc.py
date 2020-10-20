import os
from typing import Sequence, Union

import fiona

from enc.feature import Feature, supported_features
from enc.shapes import Area, Position

_path_charts = 'data', 'charts'
_path_external = 'data', 'external'
_external_chart_files = next(os.walk(os.path.join(*_path_external)))[2]
_default_depths = (0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500)
_supported_geometry = ('Polygon', 'Point')

supported_projection = 'EUREF89 UTM sone 33, 2d'
supported_regions = ('Agder', 'Hele landet', 'Møre og Romsdal', 'Nordland',
                     'Nordsjøen', 'Norge', 'Oslo', 'Rogaland', 'Svalbard',
                     'Troms og Finnmark', 'Trøndelag',
                     'Vestfold og Telemark',
                     'Vestland', 'Viken')


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
            self.region = (_Region(region),)
        elif self._is_sequence_of_strings(region):
            self.region = tuple(_Region(r) for r in region)
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
            self._write_data_to_shape_file(feature, layer)
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
        with self._shape_file_reader(feature) as file:
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
                with fiona.open(r.zip_path, 'r', layer=feature.id) as file:
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

    def _write_data_to_shape_file(self, feature, data):
        with self._shape_file_writer(feature) as file:
            for depth, shape in data:
                file.write({'properties': {'depth': depth},
                            'geometry': {'type': feature.shape_type,
                                         'coordinates': shape}})

    @staticmethod
    def _shape_file_reader(feature):
        return fiona.open(os.path.join(*_path_charts, feature.name))

    @staticmethod
    def _shape_file_writer(feature):
        path = os.path.join(*_path_charts)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, feature.name)
        driver, crs = 'ESRI Shapefile', {'init': 'epsg:25833'}
        schema = {'properties': {'depth': 'float'},
                  'geometry': feature.shape_type}

        return fiona.open(path, 'w', schema=schema, driver=driver, crs=crs)

    @staticmethod
    def _is_tuple_with_length_two(o):
        return isinstance(o, tuple) and len(o) == 2

    @staticmethod
    def _is_sequence_of_strings(o):
        return isinstance(o, Sequence) and all(isinstance(s, str) for s in o)


class _Region:
    prefix = 'Basisdata'
    data_type = 'Dybdedata'
    projection = '25833'
    suffix = 'FGDB.zip'

    def __init__(self, name: str):
        if name in supported_regions:
            if name == 'Hele landet':
                self.name = 'Norge'
            else:
                self.name = name
        else:
            raise RegionNameError(
                f"Region '{name}' not valid, possible candidates are "
                f"{supported_regions}"
            )
        self.file_name = self._validate_file_name()

    @property
    def id(self):
        string = self.name
        for s, r in [('æ', 'e'), ('ø', 'o'), ('å', 'a'), (' ', '_')]:
            string = string.replace(s, r)
        return string

    @property
    def zip_path(self):
        db_file = self.file_name.replace('.zip', '.gdb')
        return '/'.join(('zip:/', *_path_external, self.file_name, db_file))

    def _validate_file_name(self):
        for file_name in _external_chart_files:
            if self.id in file_name:
                if self._file_name_matches_template(file_name):
                    return file_name
                else:
                    raise InvalidRegionFileError(
                        f"Region '{self.name}' should have the form "
                        f"{_Region.prefix}_<int>_{self.id}_"
                        f"{_Region.projection}_{_Region.data_type}"
                        f"_{_Region.suffix}"
                    )
        else:
            raise RegionFileNotFoundError(
                f"Region '{self.name}' not found in path "
                f"'{os.path.join(*_path_external)}'"
            )

    def _file_name_matches_template(self, string):
        items = string.split('_')
        form = (items[0], items[-1], items[-2], items[-3])
        template = (self.prefix, self.suffix, self.data_type, self.projection)
        return True if form == template else False


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


class RegionNameError(NameError):
    pass


class RegionFileNotFoundError(FileExistsError):
    pass


class InvalidRegionFileError(NameError):
    pass
