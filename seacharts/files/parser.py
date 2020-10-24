from typing import Sequence

from .layer import Layer
from .region import Region


class Parser:
    default_depths = (0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500)

    def __init__(self, bounding_box, region, features, depths):
        self.bounding_box = bounding_box
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
        if depths is None:
            self.depths = self.default_depths
        elif not isinstance(features, str) and isinstance(depths, Sequence):
            self.depths = tuple(int(i) for i in depths)
        else:
            raise TypeError(
                "ENC: Depth bins should be a sequence of numbers"
            )

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

    def get_feature_layer_by_name(self, name):
        layer = next((x for x in self.layers if x.name == name), None)
        if not layer:
            raise ValueError(
                f"ENC: Feature '{name}' not found in feature layer list "
                f"{list(x.name for x in self.layers)}"
            )
        return layer
