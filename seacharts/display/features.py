from __future__ import annotations

from cartopy.feature import ShapelyFeature

import seacharts.data as data
import seacharts.display as dis
import seacharts.spatial as spl
from .colors import color_picker


class FeaturesManager:
    def __init__(self, display: dis.Display):
        self._display = display
        self.show_ownship = False
        self.show_hazards = False
        self.show_vessels = True
        self.show_arrows = True
        self._paths = [spl.Path('yellow', 1), spl.Path('pink', 2)]
        self._ownship = None
        self._horizon = None
        self._vessels = {}
        self._hazards = {}
        self._arrows = {}
        self._seabeds = {}
        self._land = None
        self._shore = None
        self._init_layers()

    @property
    def animated(self):
        return [a for a in [self._horizon,
                            *self._hazards.values(),
                            *self._arrows.values(),
                            self._paths[0].artist, self._paths[1].artist,
                            *[v['artist'] for v in self._vessels.values()],
                            self._ownship] if a]

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

    def update_waypoints(self, number, pick, coords=None):
        path = self._paths[number]
        index = path.locate_waypoint(*pick)
        if coords is not None:
            path.add_waypoint(*coords, index)
        else:
            if index is None:
                index = path.locate_edge(*pick)
                if index is None:
                    return
                else:
                    path.add_waypoint(*pick, index, edge=True)
            else:
                path.remove_waypoint(index)
        if path.artist:
            path.artist.remove()
        color = color_picker(path.color)
        path.artist = self.new_artist(path.multi_shape, color)

    def update_ownship(self):
        if self.show_ownship:
            ownship = self._display.environment.ownship
            bc = color_picker('cyan')
            hc = color_picker('full_horizon')
            if self._ownship:
                self._ownship.remove()
            if self._horizon:
                self._horizon.remove()
            self._ownship = self.new_artist(ownship.geometry, bc)
            self._horizon = self.new_artist(ownship.horizon, hc)
            if not self.show_hazards:
                self._horizon.set_visible(False)

    def update_hazards(self):
        if self.show_hazards:
            safe_area = self._display.environment.safe_area
            sectors = self._display.environment.ownship.horizon_sectors
            for color, geometry in sectors.items():
                artist = self._hazards.pop(color, None)
                if artist:
                    artist.remove()
                vessel_horizons = spl.Shape.collect(
                    [v['ship'].horizon for v in self._vessels.values()]
                )
                hazards = geometry.difference(safe_area.geometry)
                if self.show_vessels:
                    bodies = geometry.intersection(vessel_horizons)
                    hazards = hazards.union(bodies)
                artist = self._arrows.pop(color, None)
                if artist:
                    artist.remove()
                if not hazards.is_empty:
                    self._hazards[color] = self.new_artist(
                        hazards, color_picker(color)
                    )
                    if self.show_arrows:
                        arrow = self.calculate_arrow(hazards)
                        self._arrows[color] = self.new_artist(
                            arrow, color_picker('orange')
                        )

    def calculate_arrow(self, hazards):
        if not spl.Shape.is_multi(hazards):
            hazards = spl.Shape.as_multi(hazards)
        ownship = self._display.environment.ownship
        lines = []
        for polygon in list(hazards):
            near = ownship.closest_points(polygon.exterior)
            lines.append(spl.Shape.line_between(near, ownship.center))
        shortest = sorted(lines, key=lambda x: x.length)[0]
        interpolated = shortest.interpolate(
            min(ownship.dimensions[1] * 0.8, shortest.length * 0.3))
        head, base = shortest.coords[0], interpolated.coords[0]
        (x1, y1), (x2, y2) = head, base
        dx, dy = (x2 - x1) / 3, (y2 - y1) / 3
        left, right = (x2 - dy, y2 + dx), (x2 + dy, y2 - dx)
        return spl.Shape.arrow_head([(x1, y1), right, left])

    def update_vessels(self):
        if self.show_vessels:
            entries = list(data.files.read_ship_poses())
            if entries is not None and len(entries) > 0:
                new_vessels = {}
                for ship_details in entries:
                    ship_id = ship_details[0]
                    pose = ship_details[1:4]
                    color = color_picker(ship_details[4])
                    ship = spl.Ship(*pose, lon_scale=2.0, lat_scale=1.0)
                    artist = self.new_artist(ship.geometry, color)
                    if self._vessels.get(ship_id, None):
                        self._vessels.pop(ship_id)['artist'].remove()
                    new_vessels[ship_id] = dict(ship=ship, artist=artist)
                self.replace_vessels(new_vessels)

    def replace_vessels(self, new_artists):
        for vessel in self._vessels.values():
            vessel['artist'].remove()
        self._vessels = new_artists

    def toggle_vessels_visibility(self, new_state: bool = None):
        if new_state is None:
            new_state = not self.show_vessels
        self.show_vessels = new_state
        for vessel in self._vessels.values():
            artist = vessel['artist']
            artist.set_visible(not artist.get_visible())
        self.update_vessels()
        self.update_hazards()
        self._display.update_plot()

    def toggle_topography_visibility(self, new_state: bool = None):
        if new_state is None:
            new_state = not self._land.get_visible()
        self._land.set_visible(new_state)
        self._shore.set_visible(new_state)
        self._display.draw_plot()

    def toggle_ownship_visibility(self):
        self.show_ownship = not self.show_ownship
        if self.show_ownship:
            self.update_ownship()
        self._ownship.set_visible(self.show_ownship)
        self.toggle_hazards_visibility()
        self._display.update_plot()

    def toggle_hazards_visibility(self):
        self.show_hazards = not self.show_hazards
        self._horizon.set_visible(self.show_hazards)
        for artist in self._hazards.values():
            artist.set_visible(self.show_hazards)
        self.toggle_arrows_visibility(self.show_hazards)

    def toggle_arrows_visibility(self, new_state: bool = None):
        if new_state is None:
            new_state = not self.show_arrows
            self.show_arrows = new_state
        for artist in self._arrows.values():
            artist.set_visible(new_state)
        self.update_hazards()
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
