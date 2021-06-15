import fiona

from . import paths as path


class ShapefileParser:
    def __init__(self, bounding_box, file_names, verbose):
        self.bounding_box = bounding_box
        self.file_names = file_names
        self.verbose = verbose

    def read_fgdb(self, label, external_labels, depth):
        for file_name in self.file_names:
            file_path = path.external / file_name
            records = self._parse_layers(file_path, external_labels, depth)
            yield from self._parse_records(records, label)

    def read_shapefile(self, label):
        file_path = self._shapefile_path(label)
        if file_path.exists():
            yield from self._read_spatial_file(file_path)

    def _parse_layers(self, file_path, external_labels, depth):
        for label in external_labels:
            if isinstance(label, dict):
                layer, depth_label = label['layer'], label['depth']
                records = self._read_spatial_file(file_path, layer=layer)
                for record in records:
                    if record['properties'][depth_label] >= depth:
                        yield record
            else:
                yield from self._read_spatial_file(file_path, layer=label)

    def _read_spatial_file(self, file_path, **kwargs):
        with fiona.open(file_path, 'r', **kwargs) as source:
            for record in source.filter(bbox=self.bounding_box):
                yield record
        return

    def _parse_records(self, records, label):
        for i, record in enumerate(records):
            if self.verbose:
                print(f"\rNumber of {label} records read: {i + 1}", end='')
            yield record
        return

    def write(self, shape):
        geometry = shape.mapping
        file_path = self._shapefile_path(shape.label)
        with self.writer(file_path, geometry['type']) as sink:
            sink.write(self._as_record(shape.depth, geometry))

    def writer(self, file_path, geometry_type):
        return fiona.open(
            file_path, 'w',
            schema=self._as_record('int', geometry_type),
            driver='ESRI Shapefile', crs={'init': 'epsg:25833'}
        )

    @staticmethod
    def _depth_filter(depth_label, minimum_depth):
        return lambda r: r['properties'][depth_label] >= minimum_depth

    @staticmethod
    def _as_record(depth, geometry):
        return {'properties': {'depth': depth}, 'geometry': geometry}

    @staticmethod
    def _shapefile_path(label):
        return path.shapefiles / label / (label + '.shp')
