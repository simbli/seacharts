import os
import pathlib

import fiona


class Shapefile:
    driver = 'ESRI Shapefile'
    crs = {'init': 'epsg:25833'}
    path = 'data', 'shapefiles'
    directory = os.path.join(*path)

    def __init__(self, label, geometry):
        self.label = label
        self.geometry = geometry

    @property
    def file_path(self):
        return os.path.join(*self.path, self.label)

    @property
    def exists(self):
        pathlib.Path(self.directory).mkdir(parents=True, exist_ok=True)
        return os.path.isdir(self.file_path)

    @property
    def schema(self):
        return self.structure('float', self.geometry)

    @property
    def writer(self):
        return fiona.open(self.file_path, 'w', schema=self.schema,
                          driver=self.driver, crs=self.crs)

    def reader(self, path, layer):
        if path is None:
            path = self.file_path
        kwargs = {'layer': layer} if layer else {}
        return fiona.open(path, 'r', **kwargs)

    def read(self, bbox, path=None, layer=None):
        with self.reader(path, layer) as source:
            for record in source.filter(bbox=bbox):
                yield record

    def write(self, shapes):
        with self.writer as sink:
            for shape in shapes:
                sink.write(self.shape_to_record(shape))

    def shape_to_record(self, shape):
        return self.structure(shape.depth, shape.mapping)

    @staticmethod
    def structure(depth, geometry):
        return {'properties': {'depth': depth}, 'geometry': geometry}
