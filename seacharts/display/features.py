from __future__ import annotations

from cartopy.feature import ShapelyFeature

import seacharts.data as data
import seacharts.display as dis
import seacharts.spatial as spl
from .colors import color_picker


class FeaturesManager:
    def __init__(self, display: dis.Display):
        self._display = display
        self._show_hazards = True
        self._ownship = None
        self._horizon = None
        self._vessels = {}
        self._hazards = {}
        self._seabeds = {}
        self._land = None
        self._shore = None
        self._init_layers()

    @property
    def animated(self):
        return [a for a in [self._horizon, *self._hazards.values(),
                            *self._vessels.values(), self._ownship] if a]

    def _init_layers(self):
        layers = self._display.environment.hydrography.loaded_layers
        for i, layer in enumerate(layers):
            rank = layer.z_order + i
            bins = len(self._display.environment.scope.depths)
            color = color_picker(i, bins)
            artist = self.new_artist(layer.geometry, color, rank)
            self._seabeds[rank] = artist
        shore = self._display.environment.topography.shore
        color = color_picker(shore.color)
        self._shore = self.new_artist(shore.geometry, color, shore.z_order)
        land = self._display.environment.topography.land
        color = color_picker(land.color)
        self._land = self.new_artist(land.geometry, color, land.z_order)

    def new_artist(self, geometry, color, z_order=None):
        kwargs = dict(crs=self._display.crs)
        if z_order is not None:
            kwargs['zorder'] = z_order
        if isinstance(color, tuple):
            kwargs['ec'] = color[0]
            kwargs['fc'] = color[1]
        else:
            kwargs['color'] = color
        artist = self._display.axes.add_feature(
            ShapelyFeature([geometry], **kwargs)
        )
        if z_order is None:
            artist.set_animated(True)
        return artist

    def update_ownship(self):
        ownship = self._display.environment.ownship
        bc = color_picker('cyan')
        hc = color_picker('full_horizon')
        if self._ownship:
            self._ownship.remove()
        if self._horizon:
            self._horizon.remove()
        self._ownship = self.new_artist(ownship.geometry, bc)
        self._horizon = self.new_artist(ownship.horizon, hc)

    def update_hazards(self):
        if self._show_hazards:
            safe_area = self._display.environment.safe_area
            sectors = self._display.environment.ownship.horizon_sectors
            for color, geometry in sectors.items():
                artist = self._hazards.pop(color, None)
                if artist:
                    artist.remove()
                hazards = geometry.difference(safe_area.geometry)
                if not hazards.is_empty:
                    self._hazards[color] = self.new_artist(
                        hazards, color_picker(color)
                    )

    def update_vessels(self):
        entries = list(data.files.read_ship_poses())
        if entries is not None and len(entries) > 0:
            new_artists = {}
            for ship_details in entries:
                ship_id = ship_details[0]
                pose = ship_details[1:4]
                color = color_picker(ship_details[4])
                ship = spl.Ship(*pose, in_degrees=True)
                artist = self.new_artist(ship.geometry, color)
                if self._vessels.get(ship_id, None):
                    self._vessels.pop(ship_id).remove()
                new_artists[ship_id] = artist
            self.replace_vessels(new_artists)

    def replace_vessels(self, new_artists):
        for artist in self._vessels.values():
            artist.remove()
        self._vessels = new_artists

    def toggle_vessels_visibility(self):
        for artist in self._vessels.values():
            artist.set_visible(not artist.get_visible())
        self._display.update_plot()

    def toggle_land_visibility(self):
        self._land.set_visible(not self._land.get_visible())
        self._display.draw_plot()

    def toggle_shore_visibility(self):
        self._shore.set_visible(not self._shore.get_visible())
        self._display.draw_plot()

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
            self._display.draw_plot()

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
