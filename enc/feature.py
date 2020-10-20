import os
from typing import Sequence

import fiona

from enc.region import Region


class Feature:
    path_charts = 'data', 'charts'
    supported = {'seabed': ('Polygon', 'dybdeareal', 'minimumsdybde'),
                 'land': ('Polygon', 'landareal', None),
                 'rocks': ('Point', 'skjer', None),
                 'shallows': ('Point', 'grunne', 'dybde'),
                 'shore': ('Polygon', 'torrfall', None)}

    def __init__(self, name, region):
        if isinstance(name, str) and name in self.supported:
            self.name = name
        else:
            raise ValueError(
                f"Invalid feature name '{name}', "
                f"possible candidates are {self.supported}"
            )
        if isinstance(region, str):
            self.region = (Region(region),)
        elif isinstance(region, Sequence):
            self.region = tuple(Region(r) for r in region)
        else:
            raise TypeError(
                f"Invalid region format for '{region}', should be string or "
                f"sequence of strings"
            )
        self.shape_type = self.supported[name][0]
        self.id = self.supported[name][1]
        self.depth_label = self.supported[name][2]

    def read_shapefile(self, bounding_box):
        with self.shapefile_reader() as file:
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
        with self.shapefile_writer() as file:
            for depth, shape in data:
                file.write({'properties': {'depth': depth},
                            'geometry': {'type': self.shape_type,
                                         'coordinates': shape}})

    def fgdb_reader(self, region):
        return fiona.open(region.zip_path, 'r', layer=self.id)

    def shapefile_reader(self):
        return fiona.open(os.path.join(*self.path_charts, self.name))

    def shapefile_writer(self):
        path = os.path.join(*self.path_charts)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, self.name)
        driver, crs = 'ESRI Shapefile', {'init': 'epsg:25833'}
        schema = {'properties': {'depth': 'float'},
                  'geometry': self.shape_type}
        return fiona.open(path, 'w', schema=schema, driver=driver, crs=crs)

    @classmethod
    def all_supported_features(cls, region):
        return tuple(Feature(f, region) for f in cls.supported)
