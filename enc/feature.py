import os
from typing import Sequence

import fiona

from enc.region import Region

_path_charts = 'data', 'charts'
_supported_terrain = {'seabed': ('Polygon', 'dybdeareal', 'minimumsdybde'),
                      'land': ('Polygon', 'landareal', None),
                      'rocks': ('Point', 'skjer', None),
                      'shallows': ('Point', 'grunne', 'dybde'),
                      'shore': ('Polygon', 'torrfall', None)}
supported_features = tuple(f for f in _supported_terrain.keys())


class Feature:
    def __init__(self, name, region):
        if isinstance(name, str) and name in supported_features:
            self.name = name
        else:
            raise FeatureValueError(
                f"Feature name '{name}' not valid, "
                f"possible candidates are {supported_features}"
            )
        if isinstance(region, str):
            self.region = (Region(region),)
        elif isinstance(region, Sequence):
            self.region = tuple(Region(r) for r in region)
        else:
            raise RegionFormatError(
                f"Region '{region}' not valid, should be string or "
                f"sequence of strings"
            )
        self.shape_type = _supported_terrain[name][0]
        self.id = _supported_terrain[name][1]
        self.depth_label = _supported_terrain[name][2]

    def read_shapefile(self, bounding_box):
        with self.shapefile_reader as file:
            for record in file.filter(bbox=bounding_box):
                yield self.parse_record(record)

    def load_all_regional_shapes(self, bounding_box):
        for r in self.region:
            if self.id in fiona.listlayers(r.zip_path):
                with self.fgdb_reader(r) as file:
                    for record in file.filter(bbox=bounding_box):
                        yield self.parse_record(record)

    def parse_record(self, record):
        if self.depth_label:
            depth = record['properties'][self.depth_label]
        else:
            depth = 0
        coords = record['geometry']["coordinates"]
        if self.shape_type == 'Point':
            shape = coords
        else:
            shape = coords[0]
        return depth, shape

    def write_data_to_shapefile(self, data):
        with self.shapefile_writer as file:
            for depth, shape in data:
                file.write({'properties': {'depth': depth},
                            'geometry': {'type': self.shape_type,
                                         'coordinates': shape}})

    def fgdb_reader(self, region):
        return fiona.open(region.zip_path, 'r', layer=self.id)

    @property
    def shapefile_reader(self):
        return fiona.open(os.path.join(*_path_charts, self.name))

    @property
    def shapefile_writer(self):
        path = os.path.join(*_path_charts)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, self.name)
        driver, crs = 'ESRI Shapefile', {'init': 'epsg:25833'}
        schema = {'properties': {'depth': 'float'},
                  'geometry': self.shape_type}
        return fiona.open(path, 'w', schema=schema, driver=driver, crs=crs)

    @staticmethod
    def all_supported_features(region):
        return tuple(Feature(f, region) for f in supported_features)

    @staticmethod
    def is_supported(name):
        if name in supported_features:
            return True
        raise FeatureValueError(
            f"Feature name '{name}' not valid, "
            f"possible candidates are {supported_features}"
        )


class FeatureValueError(ValueError):
    pass


class RegionFormatError(TypeError):
    pass
