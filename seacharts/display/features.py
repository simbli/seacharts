"""
Contains the FeaturesManager class for plotting spatial features on a display.
"""
import shapely.geometry as geo
from cartopy.feature import ShapelyFeature
from matplotlib.lines import Line2D
from shapely.geometry import MultiLineString

from seacharts import shapes, core
from .colors import color_picker


# noinspection PyProtectedMember
class FeaturesManager:
    def __init__(self, display):
        self._display = display
        self.show_vessels = True
        self._vessels = {}
        self._seabeds = {}
        self._land = None
        self._shore = None
        self._extra_layers = {}
        self._number_of_layers = len(self._display._environment.get_layers())
        self._next_z_order = self._number_of_layers * -1
        self._init_layers()

    def _init_layers(self):
        seabeds = list(self._display._environment.map.bathymetry.values())
        for i, seabed in enumerate(seabeds):
            if not seabed.geometry.is_empty:
                bins = len(self._display._environment.scope.depths)
                color = color_picker(i, bins)
                self._seabeds[i] = self.assign_artist(seabed, self._get_next_z_order(), color)

        shore = self._display._environment.map.shore
        color = color_picker(shore.__class__.__name__)
        self._shore = self.assign_artist(shore, self._get_next_z_order(), color)

        land = self._display._environment.map.land
        color = color_picker(land.__class__.__name__)
        self._land = self.assign_artist(land, self._get_next_z_order(), color)

        for i, extra_layer in enumerate(self._display._environment.extra_layers.loaded_regions):
            self._extra_layers[i] = self.assign_artist(extra_layer, self._get_next_z_order(), extra_layer.color)

        center = self._display._environment.scope.extent.center
        size = self._display._environment.scope.extent.size
        geometry = shapes.Rectangle(
            *center, width=size[0] / 2, heading=0, height=size[1] / 2
        ).geometry
        color = (color_picker("black")[0], "none")
        self.new_artist(geometry, color, z_order=self._get_next_z_order(), linewidth=3)

    def _get_next_z_order(self) -> int:
        z_order = self._next_z_order
        self._next_z_order += 1
        return z_order

    @property
    def animated(self):
        return [a for a in [v["artist"] for v in self._vessels.values()] if a]

    def assign_artist(self, layer, z_order, color):
        if isinstance(layer.geometry, MultiLineString):
            artist = []
            for line in layer.geometry.geoms:
                artist.append(self.new_line_artist(line, color, z_order))
        else:
            artist = self.new_artist(layer.geometry, color, z_order=z_order)
        return artist

    def new_artist(self, geometry, color, z_order=None, **kwargs):
        kwargs["crs"] = self._display.crs
        if z_order is not None:
            kwargs["zorder"] = z_order
        if isinstance(color, tuple):
            kwargs["ec"] = color[0]
            kwargs["fc"] = color[1]
        else:
            kwargs["color"] = color
        artist = self._display.axes.add_feature(ShapelyFeature([geometry], **kwargs))
        if z_order is None:
            artist.set_animated(True)
        return artist

    def new_line_artist(self, line_geometry, color, z_order=None, **kwargs):
        x, y = line_geometry.xy
        # TODO: confirm if linewidth 2 wont cause errors in research, linewidth=1 is not visible
        line = self._display.axes.add_line(Line2D(x, y, color=color, linewidth=kwargs.get('linewidth', 2)))
        if z_order is None:
            line.set_animated(True)
        else:
            line.set_zorder(z_order)
        return line

    def add_arrow(
        self, start, end, color_name, buffer, fill, head_size, linewidth, linestyle
    ):
        if buffer is None:
            buffer = 5
        if head_size is None:
            head_size = 50
        body = shapes.Arrow(start=start, end=end, width=buffer).body(head_size)
        self.add_overlay(body, color_name, fill, linewidth, linestyle)

    def add_circle(self, center, radius, color_name, fill, linewidth, linestyle, alpha):
        geometry = shapes.Circle(*center, radius).geometry
        self.add_overlay(geometry, color_name, fill, linewidth, linestyle, alpha)

    def add_line(self, points, color_name, buffer, linewidth, linestyle, marker):
        if buffer is None:
            buffer = 5
        if buffer == 0:
            x_coordinates, y_coordinates = zip(*points)
            self._display.axes.plot(
                x_coordinates,
                y_coordinates,
                color=color_picker(color_name)[0],
                linewidth=linewidth,
                linestyle=linestyle,
                marker=marker,
                transform=self._display.crs,
            )
        else:
            geometry = shapes.Line(points=points).geometry.buffer(buffer)
            self.add_overlay(geometry, color_name, True, linewidth, linestyle)

    def add_polygon(
        self, shape, color, interiors, fill, linewidth, linestyle, alpha=1.0
    ):
        try:
            if isinstance(shape, geo.MultiPolygon) or isinstance(
                shape, geo.GeometryCollection
            ):
                shape = list(shape.geoms)
            else:
                shape = list(shape)
        except TypeError:
            shape = [shape]
        if isinstance(shape[0], tuple) or isinstance(shape[0], list):
            shape = [shape]
        for geometry in shape:
            geometry = shapes.Area.new_polygon(geometry, interiors)
            self.add_overlay(geometry, color, fill, linewidth, linestyle, alpha)

    def add_rectangle(
        self, center, size, color_name, rotation, fill, linewidth, linestyle, alpha
    ):
        geometry = shapes.Rectangle(
            *center, heading=rotation, width=size[0], height=size[1]
        ).geometry
        self.add_overlay(geometry, color_name, fill, linewidth, linestyle, alpha)

    def add_overlay(self, geometry, color_name, fill, linewidth, linestyle, alpha=1.0):
        color = color_picker(color_name)
        if fill is False:
            color = color[0], "none"
        kwargs = {}
        if linewidth is not None:
            kwargs["linewidth"] = linewidth
        if linestyle is not None:
            kwargs["linestyle"] = linestyle
        kwargs["alpha"] = alpha
        self.new_artist(geometry, color, 0, **kwargs)

    def update_vessels(self):
        if self.show_vessels:
            entries = list(core.files.read_ship_poses())
            if entries is not None:
                new_vessels = {}
                for ship_details in entries:
                    ship_id = ship_details[0]
                    pose = ship_details[1:4]
                    other = ship_details[4]
                    if len(other) > 0 and isinstance(other[0], str):
                        color = color_picker(other[0])
                    else:
                        color = color_picker("red")
                    kwargs = dict(
                        scale=float(other[1]) if len(other) > 1 else 1.0,
                        lon_scale=float(other[2]) if len(other) > 2 else 2.0,
                        lat_scale=float(other[3]) if len(other) > 3 else 1.0,
                    )
                    ship = shapes.Ship(*pose, **kwargs)
                    artist = self.new_artist(ship.geometry, color)
                    if self._vessels.get(ship_id, None):
                        self._vessels.pop(ship_id)["artist"].remove()
                    new_vessels[ship_id] = dict(ship=ship, artist=artist)
                self.replace_vessels(new_vessels)

    def replace_vessels(self, new_artists):
        for vessel in self._vessels.values():
            vessel["artist"].remove()
        self._vessels = new_artists

    def toggle_vessels_visibility(self, new_state: bool = None):
        if new_state is None:
            new_state = not self.show_vessels
        self.show_vessels = new_state
        for vessel in self._vessels.values():
            artist = vessel["artist"]
            artist.set_visible(not artist.get_visible())
        self.update_vessels()
        self._display.update_plot()

    @staticmethod
    def set_visibility(artist, new_state):
        if not isinstance(artist, list):
            artist.set_visible(new_state)
        else:
            for line in artist:
                line.set_visible(new_state)

    def toggle_topography_visibility(self, new_state: bool = None):
        if new_state is None:
            new_state = not self._land.get_visible()
        self.set_visibility(self._land, new_state)
        self.set_visibility(self._shore, new_state)
        self._display.redraw_plot()

    def show_top_hidden_layer(self):
        artists = self._z_sorted_seabeds(descending=False)
        self._toggle_next_visibility_layer(artists, visibility=True)

    def hide_top_visible_layer(self):
        artists = self._z_sorted_seabeds(descending=False)
        self._toggle_next_visibility_layer(artists, visibility=False)

    def hide_bottom_visible_layer(self):
        artists = self._z_sorted_seabeds(descending=True)
        self._toggle_next_visibility_layer(artists, visibility=False)

    def show_bottom_hidden_layer(self):
        artists = self._z_sorted_seabeds(descending=True)
        self._toggle_next_visibility_layer(artists, visibility=True)

    def _toggle_next_visibility_layer(self, artists, visibility):
        if self._any_toggleable_layer(artists, not visibility):
            artist = self._next_visibility_layer(artists, not visibility)
            artist.set_visible(visibility)
            self._display.redraw_plot()

    def _z_sorted_seabeds(self, descending=False):
        artist_keys = sorted(self._seabeds, reverse=descending)
        return [self._seabeds[key] for key in artist_keys]

    @staticmethod
    def _any_toggleable_layer(artists, visible):
        return any([a.get_visible() is visible for a in artists])

    @staticmethod
    def _next_visibility_layer(artists, visibility):
        return next(a for a in artists if a.get_visible() is visibility)

    @staticmethod
    def vessels_to_file(vessel_poses: list[tuple]) -> None:
        core.files.write_rows_to_csv(
            [("id", "x", "y", "heading", "color")] + vessel_poses,
            core.paths.vessels,
        )
