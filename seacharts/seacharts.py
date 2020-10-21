from typing import Sequence, Union

from .parser import Parser


class ENC:
    default_origin = (38100, 6948700)
    default_window_size = (20000, 16000)
    default_region = 'Møre og Romsdal'

    def __init__(self,
                 origin: tuple = default_origin,
                 window_size: tuple = default_window_size,
                 region: Union[str, Sequence] = default_region,
                 parse_new_map_data: bool = False,
                 features: Sequence = None,
                 depths: Sequence = None):

        self.parser = Parser(origin, window_size, region, features, depths)
        self.parser.update_charts_data(parse_new_map_data)

    def read_feature_coordinates(self, feature):
        return self.parser.read_feature_coordinates(feature)

    def read_feature_shapes(self, feature):
        return self.parser.read_feature_shapes(feature)
