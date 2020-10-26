from .shapes import Position


class Rocks(Position):
    layer_label = 'skjer'
    depth_label = None
    pass


class Shallows(Position):
    layer_label = 'grunne'
    depth_label = 'dybde'
    pass
