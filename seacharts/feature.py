import os

import fiona


class Feature:
    path_charts = 'data', 'charts'
    supported = {'seabed': ('Polygon', 'dybdeareal', 'minimumsdybde'),
                 'land': ('Polygon', 'landareal', None),
                 'rocks': ('Point', 'skjer', None),
                 'shallows': ('Point', 'grunne', 'dybde'),
                 'shore': ('Polygon', 'torrfall', None)}

    def __init__(self, name):
        if isinstance(name, str) and name in self.supported:
            self.name = name
        else:
            raise ValueError(
                f"ENC: Invalid feature name '{name}', "
                f"possible candidates are {self.supported}"
            )
        self.shape_type = self.supported[name][0]
        self.id = self.supported[name][1]
        self.depth_label = self.supported[name][2]
        self.shapefile_path = os.path.join(*self.path_charts, self.name)

    @property
    def shapefile_exists(self):
        return os.path.isdir(self.shapefile_path)

    def read_shapefile(self, bounding_box):
        with fiona.open(self.shapefile_path) as file:
            for record in file.filter(bbox=bounding_box):
                yield record

    def select_data(self, record, external_label=False):
        label = self.depth_label if external_label else 'depth'
        depth = record['properties'][label] if label else 0
        coords = record['geometry']['coordinates']
        if self.shape_type == 'Polygon':
            coords = coords[0]
        return depth, coords

    def write_data_to_shapefile(self, data):
        with self.shapefile_writer() as file:
            for depth, coords in data:
                file.write({'properties': {'depth': depth},
                            'geometry': {'type': self.shape_type,
                                         'coordinates': coords}})

    def shapefile_writer(self):
        path = os.path.join(*self.path_charts)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, self.name)
        driver, crs = 'ESRI Shapefile', {'init': 'epsg:25833'}
        schema = {'properties': {'depth': 'float'},
                  'geometry': self.shape_type}
        return fiona.open(path, 'w', schema=schema, driver=driver, crs=crs)
