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


class FeatureValueError(ValueError):
    pass
