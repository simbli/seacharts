from typing import Sequence

from seacharts.shapes import Area, Position
from .layer import Layer
from .region import Region


class Parser:
    default_depths = (0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500)
    supported_projection = 'EUREF89 UTM sone 33, 2d'
    supported_geometry = ('Polygon', 'Point')

    def __init__(self, origin, window_size, region, features, depths):
        if isinstance(origin, tuple) and len(origin) == 2:
            self.origin = origin
        else:
            raise TypeError(
                "ENC: Origin should be a tuple of size two"
            )
        if isinstance(window_size, tuple) and len(window_size) == 2:
            self.window_size = window_size
        else:
            raise TypeError(
                "ENC: Window size should be a tuple of size two"
            )
        if depths is None:
            self.depths = self.default_depths
        elif not isinstance(features, str) and isinstance(depths, Sequence):
            self.depths = tuple(int(i) for i in depths)
        else:
            raise TypeError(
                "ENC: Depth bins should be a sequence of numbers"
            )
        if isinstance(region, str) or isinstance(region, Sequence):
            self.region = Region(region)
        else:
            raise TypeError(
                f"ENC: Invalid region format for '{region}', should be "
                f"string or sequence of strings"
            )
        if features is None:
            self.layers = list(Layer(x) for x in Layer.supported)
        elif isinstance(features, Sequence):
            if all(isinstance(x, Layer) for x in features):
                self.layers = list(features)
            else:
                self.layers = list(Layer(x) for x in features)
        else:
            raise TypeError(
                f"ENC: Invalid feature layer format for '{features}', "
                f"should be a sequence of strings or {Layer} objects"
            )
        tr_corner = (i + j for i, j in zip(self.origin, self.window_size))
        self.bounding_box = *self.origin, *tr_corner

    def update_charts_data(self, new_data):
        if not new_data:
            for layer in self.layers:
                if not layer.shapefile_exists:
                    print(f"ENC: Missing shapefile for feature layer "
                          f"'{layer.name}', initializing new parsing of "
                          f"downloaded ENC data")
                    new_data = True
                    break
        if new_data:
            self.process_external_data()

    def process_external_data(self):
        print("ENC: Processing features from region...")
        for layer in self.layers:
            records = self.region.read_fgdb_files(layer, self.bounding_box)
            data = list(layer.select_data(r, True) for r in records)
            layer.write_data_to_shapefile(data)
            print(f"  Feature layer extracted: {layer.name}")
        print("External data processing complete\n")

    def extract_coordinates(self, layer):
        if not isinstance(layer, Layer):
            layer = self.get_feature_layer_by_name(layer)
        records = layer.read_shapefile(self.bounding_box)
        data = list(layer.select_data(r) for r in records)
        if len(data) == 0:
            raise ValueError(
                f"ENC: Feature layer {layer.name} returned no shapes within"
                f"bounding box {self.bounding_box}"
            )
        return data

    def extract_shapes(self, layer):
        data = self.extract_coordinates(layer)
        if isinstance(data[0][1], tuple):
            return [Position(point, depth) for depth, point in data]
        else:
            return [Area(points, depth) for depth, points in data]

    def get_feature_layer_by_name(self, name):
        layer = next((x for x in self.layers if x.name == name), None)
        if not layer:
            raise ValueError(
                f"ENC: Feature '{name}' not found in feature layer list "
                f"{list(x.name for x in self.layers)}"
            )
        return layer
