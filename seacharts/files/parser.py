from typing import Sequence

from .filegdb import FileGDB
from .shapefile import Shapefile


class Parser:
    default_depths = (0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500)

    def __init__(self, bounding_box, features, region, depths):
        self.bounding_box = bounding_box
        self.shapefiles = tuple(Shapefile(f) for f in features)
        if isinstance(region, str) or isinstance(region, Sequence):
            self.region = FileGDB(region)
        else:
            raise TypeError(
                f"ENC: Invalid region format for '{region}', should be "
                f"string or sequence of strings"
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

    def extract_coordinates(self, feature):
        shapefile = next((shp for shp in self.shapefiles
                          if shp.name == feature), None)
        if not shapefile:
            raise ValueError(
                f"ENC: Feature '{feature}' not found in shapefile list "
                f"{list(x.name for x in self.shapefiles)}"
            )
        records = shapefile.read(self.bounding_box)
        data = list(shapefile.select_data(r) for r in records)
        if len(data) == 0:
            raise ValueError(
                f"ENC: Feature layer {shapefile.name} returned no shapes "
                f"within bounding box {self.bounding_box}"
            )
        return data
