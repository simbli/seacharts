import os

import fiona


class Shapefile:
    path_charts = 'data', 'charts'

    def __init__(self, feature):
        self.feature = feature
        self.name = feature.__name__.lower()
        self.path = os.path.join(*self.path_charts, self.name)

    @property
    def exists(self):
        return os.path.isdir(self.path)

    def read(self, bounding_box):
        with fiona.open(self.path) as file:
            for record in file.filter(bbox=bounding_box):
                yield self.select_data(record)

    def select_data(self, record, external_label=False):
        label = self.feature.depth_label if external_label else 'depth'
        depth = record['properties'][label] if label else 0
        coords = record['geometry']['coordinates']
        if self.feature.shape == 'Polygon':
            coords = coords[0]
        return depth, coords

    def write_data(self, data):
        with self.writer() as file:
            for depth, coords in data:
                file.write({'properties': {'depth': depth},
                            'geometry': {'type': self.feature.shape,
                                         'coordinates': coords}})

    def writer(self):
        path = os.path.join(*self.path_charts)
        if not os.path.exists(path):
            os.makedirs(path)
        path = os.path.join(path, self.name)
        driver, crs = 'ESRI Shapefile', {'init': 'epsg:25833'}
        schema = {'properties': {'depth': 'float'},
                  'geometry': self.feature.shape}
        return fiona.open(path, 'w', schema=schema, driver=driver, crs=crs)
