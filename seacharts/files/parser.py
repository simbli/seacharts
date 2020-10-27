from typing import Sequence

from .filegdb import FileGDB
from .shapefile import Shapefile


class Parser:
    def __init__(self, bounding_box, region, depths):
        self.bounding_box = bounding_box
        self.shapefiles = ()
        self.depths = depths
        if isinstance(region, str) or isinstance(region, Sequence):
            self.region = FileGDB(region)
        else:
            raise TypeError(
                f"ENC: Invalid region format for '{region}', should be "
                f"string or sequence of strings"
            )

    def update_charts_data(self, features, new_data):
        self.shapefiles = tuple(Shapefile(f) for f in features)
        if not new_data:
            for shapefile in self.shapefiles:
                if not shapefile.exists:
                    print(f"ENC: Missing shapefile for feature layer "
                          f"'{shapefile.name}', initializing new parsing of "
                          f"downloaded ENC data")
                    new_data = True
                    break
        if new_data:
            self.process_external_data()

    def process_external_data(self):
        print("ENC: Processing features from region...")
        for shapefile in self.shapefiles:
            layer_name = shapefile.feature.layer_label
            records = self.region.read_files(layer_name, self.bounding_box)
            data = list(shapefile.select_data(r, True) for r in records)
            shapefile.write_data(data)
            print(f"  Feature layer extracted: {shapefile.name}")
        print("External data processing complete\n")

    def load(self, feature):
        data = tuple(Shapefile(feature).read(self.bounding_box))
        if len(data) == 0:
            raise ValueError(
                f"ENC: Feature layer {feature.__name__} returned no "
                f"shapes within bounding box {self.bounding_box}"
            )
        return [feature(shape, depth) for depth, shape in data]
