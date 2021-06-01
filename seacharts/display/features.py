from __future__ import annotations

from cartopy.feature import ShapelyFeature

import seacharts.data as data
import seacharts.display as dis
import seacharts.spatial as spl
from . import colors


class FeaturesManager:
    def __init__(self, display: dis.Display):
        self._display = display
        self._vessels = {}
        self._seabeds = {}
        self._land = None
        self._shore = None
        self._init_layers()

    def _init_layers(self):
        layers = self._display.environment.hydrography.loaded_layers
        for i, layer in enumerate(layers):
            rank = layer.z_order + i
            bins = len(self._display.environment.scope.depths)
            color = colors.color_picker(i, bins)
            artist = self.new_artist(layer.geometry, color, rank)
            self._seabeds[rank] = artist
        shore = self._display.environment.topography.shore
        color = colors.color_picker(shore.color)
        self._shore = self.new_artist(shore.geometry, color, shore.z_order)
        land = self._display.environment.topography.land
        color = colors.color_picker(land.color)
        self._land = self.new_artist(land.geometry, color, land.z_order)

    def new_artist(self, geometry, color, z_order, animated=False):
        kwargs = dict(crs=self._display.crs, zorder=z_order, animated=animated)
        if isinstance(color, tuple):
            kwargs['ec'] = color[0]
            kwargs['fc'] = color[1]
        else:
            kwargs['color'] = color
        return self._display.axes.add_feature(
            ShapelyFeature([geometry], **kwargs)
        )

    def copy_canvas(self):
        self._display.update_plot()
        return self._display.figure.canvas.copy_from_bbox(
            self._display.figure.bbox
        )

    def update(self):
        poses = list(data.files.read_ship_poses())
        if poses is not None and len(poses) > 0:
            self.remove_vessels()
            for ship_details in poses:
                ship_id = ship_details[0]
                pose = ship_details[1:4]
                color = colors.color_picker(ship_details[4])
                ship = spl.Ship(*pose, in_degrees=True)
                artist = self.new_artist(ship.geometry, color, 100 + ship_id)
                self._vessels[ship_id] = artist
            self._display.update_plot()

    def remove_vessels(self):
        for artist in self._vessels.values():
            artist.set_visible(False)
            artist.remove()
        self._vessels = {}

    def toggle_vessels_visibility(self):
        for artist in self._vessels.values():
            artist.set_visible(not artist.get_visible())
        self._display.update_plot()

    def toggle_land_visibility(self):
        self._land.set_visible(not self._land.get_visible())
        self._display.update_plot()

    def toggle_shore_visibility(self):
        self._shore.set_visible(not self._shore.get_visible())
        self._display.update_plot()

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
            self._display.update_plot()

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
    def vessels_to_file(vessel_poses: list):
        data.files.write_rows_to_csv(
            [('id', 'easting', 'northing', 'heading', 'color')] + vessel_poses
        )
