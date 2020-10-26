from .shapes import Area


class Land(Area):
    layer_label = 'landareal'
    depth_label = None
    pass


class Shore(Area):
    layer_label = 'torrfall'
    depth_label = None
    pass
