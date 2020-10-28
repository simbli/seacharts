from .shapes import Area, Position


class Seabed(Area):
    layer_label = 'dybdeareal'
    depth_label = 'minimumsdybde'
    pass


class Land(Area):
    layer_label = 'landareal'
    depth_label = None
    pass


class Shore(Area):
    layer_label = 'torrfall'
    depth_label = None
    pass


class Rocks(Position):
    layer_label = 'skjer'
    depth_label = None
    pass


class Shallows(Position):
    layer_label = 'grunne'
    depth_label = 'dybde'
    pass


class Ship(Position):
    ship_dimensions = (13.6, 74.7)

    def __init__(self, center, heading=0.0, scale=1.0):
        if isinstance(center, Position):
            self.center = center
        else:
            raise TypeError(
                f"Ship center should be a {Position} object"
            )
        if isinstance(heading, int) or isinstance(heading, float):
            self.heading = heading
        else:
            raise TypeError(
                f"Ship heading should be a number in degrees"
            )
        x, y = center.coordinates
        w, h = (i * scale for i in self.ship_dimensions)
        x_min, x_max = x - w / 2, x + w / 2
        y_min, y_max = y - h / 2, y + h / 2 - w
        left_aft, right_aft = (x_min, y_min), (x_max, y_min)
        left_bow, right_bow = (x_min, y_max), (x_max, y_max)
        points = (left_aft, left_bow, (x, y + h / 2), right_aft, right_bow)
        angle, origin = -self.heading, self.center.coordinates
        super().__init__(Area(points).rotate(angle, origin))

    @property
    def coordinates(self):
        return self.center.coordinates
