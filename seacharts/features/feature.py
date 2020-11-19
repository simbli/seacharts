import fiona
from cartopy.crs import UTM
from cartopy.feature import ShapelyFeature

from .. import settings as config
from ..features.shapes import Area, Position


class Feature(ShapelyFeature):
    crs = UTM(33)

    def __init__(self, geometries=(), **kwargs):
        self.color = config.color(self.name)
        shp = self.name.lower()
        self._file_path = config.path_shapefiles / shp / (shp + '.shp')
        super().__init__(geometries, self.crs, color=self.color, **kwargs)

    def __getitem__(self, item):
        return self._geoms[item]

    @property
    def name(self):
        return self.__class__.__name__

    @property
    def shapefile_exists(self):
        return self._file_path.is_file()

    @property
    def shape(self):
        raise NotImplementedError

    @property
    def depth_label(self):
        raise NotImplementedError

    @property
    def layer_label(self):
        raise NotImplementedError

    def load(self, bbox, external=None):
        self._geoms = tuple(self.read_shapes(bbox, external))

    def read_shapes(self, bbox, external):
        paths = external if external else [None]
        layer = self.layer_label if external else None
        for path in paths:
            records = self.read_shapefile(bbox, path, layer)
            for record in records:
                yield self.record_to_shape(record, external)

    def read_shapefile(self, bbox, path=None, layer=None):
        if path is None:
            path = self._file_path
        kwargs = {'layer': layer} if layer else {}
        with fiona.open(path, 'r', **kwargs) as source:
            for record in source.filter(bbox=bbox):
                yield record

    def record_to_shape(self, record, external_label):
        label = self.depth_label if external_label else 'depth'
        depth = record['properties'][label] if label else 0
        coords = record['geometry']['coordinates']
        if self.shape.type == 'Polygon':
            coords = coords[0][0] if external_label else coords[0]
        return self.shape(coords, depth)

    def write_to_shapefile(self):
        writer = fiona.open(
            self._file_path, 'w',
            schema=self.record_structure('float', self.shape.type),
            driver='ESRI Shapefile', crs={'init': 'epsg:25833'}
        )
        with writer as sink:
            for shape in self._geoms:
                sink.write(
                    self.record_structure(shape.depth, shape.mapping)
                )

    @staticmethod
    def record_structure(depth, geometry):
        return {'properties': {'depth': depth}, 'geometry': geometry}


class Seabed(Feature):
    shape = Area
    layer_label = 'dybdeareal'
    depth_label = 'minimumsdybde'


class Land(Feature):
    shape = Area
    layer_label = 'landareal'
    depth_label = None
    pass


class Shore(Feature):
    shape = Area
    layer_label = 'torrfall'
    depth_label = None
    pass


class Rocks(Feature):
    shape = Position
    layer_label = 'skjer'
    depth_label = None
    pass


class Shallows(Feature):
    shape = Position
    layer_label = 'grunne'
    depth_label = 'dybde'
    pass


class Ship(Feature):
    shape = Position
    layer_label = None
    depth_label = None
    default_scale = 1.0
    ship_dimensions = (16, 80)
    heading_in_radians = True

    def __init__(self, x, y, heading, origin, scale=None):
        utm_x, utm_y = x + origin[0], y + origin[1]
        self.center = Position((utm_x, utm_y))
        self.heading = heading
        if scale is None:
            self.scale = self.default_scale
        elif isinstance(scale, float):
            self.scale = scale
        else:
            raise TypeError(
                f"Ship scale should be a float"
            )
        super().__init__(geometries=self.create_hull())

    @property
    def coords(self):
        return self.center.coords[0]

    @property
    def hull(self):
        return self._geoms

    def create_hull(self):
        x, y = self.center.coords[0]
        w, h = (i * self.scale for i in self.ship_dimensions)
        x_min, x_max = x - w / 2, x + w / 2
        y_min, y_max = y - h / 2, y + h / 2 - w
        left_aft, right_aft = (x_min, y_min), (x_max, y_min)
        left_bow, right_bow = (x_min, y_max), (x_max, y_max)
        points = [left_aft, left_bow, (x, y + h / 2), right_bow, right_aft]
        if self.heading_in_radians:
            angle = -self.heading * 180 / 3.14
        else:
            angle = -self.heading
        return Area(points).rotate(angle, self.center.coords[0]),

    def update_pose(self, new_ship):
        self.center = new_ship.center
        self._geoms = new_ship.hull
