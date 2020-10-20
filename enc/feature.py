import os

import fiona

_path_charts = 'data', 'charts'
_supported_terrain = {'seabed': ('Polygon', 'dybdeareal', 'minimumsdybde'),
                      'land': ('Polygon', 'landareal', None),
                      'rocks': ('Point', 'skjer', None),
                      'shallows': ('Point', 'grunne', 'dybde'),
                      'shore': ('Polygon', 'torrfall', None)}
supported_features = tuple(f for f in _supported_terrain.keys())


class Feature:
    def __init__(self, name: str):
        if isinstance(name, str) and name in supported_features:
            self.name = name
        else:
            raise FeatureValueError(
                f"Feature name '{name}' not valid, possible candidates are "
                f"{supported_features}"
            )
        self.shape_type = _supported_terrain[name][0]
        self.id = _supported_terrain[name][1]
        self.depth_label = _supported_terrain[name][2]

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

    def write_data_to_shapefile(self, data):
        with self.shapefile_writer as file:
            for depth, shape in data:
                file.write({'properties': {'depth': depth},
                            'geometry': {'type': self.shape_type,
                                         'coordinates': shape}})


class FeatureValueError(ValueError):
    pass
