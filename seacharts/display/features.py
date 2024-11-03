"""
Contains the FeaturesManager class for plotting spatial features on a display.
"""
import shapely.geometry as geo
from cartopy.feature import ShapelyFeature
from matplotlib.lines import Line2D
from shapely.geometry import MultiLineString, MultiPolygon

from seacharts import shapes, core
from .colors import color_picker


# noinspection PyProtectedMember
class FeaturesManager:
    """
    The FeaturesManager class is responsible for managing and rendering spatial features 
    on a given display. This includes seabeds, land, shorelines, and vessels. It also 
    provides methods for adding various geometric shapes, updating vessel positions, 
    and managing the visibility of different layers.

    Attributes:
        _display (object): The display object that this FeaturesManager interacts with.
        show_vessels (bool): A flag indicating whether vessel features should be displayed.
        _vessels (dict): A dictionary storing vessel features keyed by their IDs.
        _seabeds (dict): A dictionary storing seabed features.
        _land (object): The land feature object.
        _shore (object): The shore feature object.
        _extra_layers (dict): A dictionary for additional layers beyond seabeds and land.
        _number_of_layers (int): The total number of layers in the display's environment.
        _next_z_order (int): The next z-order value to be used for layering features.
    """
    def __init__(self, display):
        """
        Initializes the FeaturesManager with a specified display object and 
        prepares spatial features for rendering.

        :param display: The display object that will be managed by this FeaturesManager.
        """
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
        """
        Initializes the spatial feature layers such as seabeds, land, shore, and 
        any extra layers from the display's environment. It also sets their 
        corresponding z-orders for rendering.
        """
        seabeds = list(self._display._environment.map.bathymetry.values())
        for i, seabed in enumerate(seabeds):
            if not seabed.geometry.is_empty:
                bins = len(self._display._environment.scope.depths)
                color = color_picker(i, bins)
                self._seabeds[i] = self.assign_artist(seabed, self._get_next_z_order(), color)

        # Determine z-orders for shore and land
        z_orders = [self._get_next_z_order(), self._get_next_z_order()]
        shore = self._display._environment.map.shore
        if isinstance(shore.geometry, MultiPolygon):
            # if shore is multipolygon (for fgdb) we draw it beneath the land
            shore_z_order = z_orders[0] # Shore drawn beneath land
            land_z_order = z_orders[1]
        else:
            # if shore is multilinestring we draw it as edges for land
            shore_z_order = z_orders[1] # Shore drawn as edges for land
            land_z_order = z_orders[0]

        # creating shore 
        color = color_picker(shore.__class__.__name__)
        self._shore = self.assign_artist(shore, shore_z_order, color)

        # creating land
        land = self._display._environment.map.land
        color = color_picker(land.__class__.__name__)
        self._land = self.assign_artist(land, land_z_order, color)

        # creating extra layers
        for i, extra_layer in enumerate(self._display._environment.extra_layers.loaded_regions):
            self._extra_layers[i] = self.assign_artist(extra_layer, self._get_next_z_order(), extra_layer.color)

        # creating borders of bounding box
        center = self._display._environment.scope.extent.center
        size = self._display._environment.scope.extent.size
        geometry = shapes.Rectangle(
            *center, width=size[0] / 2, heading=0, height=size[1] / 2
        ).geometry
        color = (color_picker("black")[0], "none")
        self.new_artist(geometry, color, z_order=self._get_next_z_order(), linewidth=3)

    def _get_next_z_order(self) -> int:
        """
        Retrieves the next z-order for layering features and increments the z-order counter.

        :return: The next z-order value.
        """
        z_order = self._next_z_order
        self._next_z_order += 1
        return z_order

    @property
    def animated(self):
        """
        Returns a list of currently animated vessel artists.

        :return: A list of animated artists corresponding to vessels.
        """
        return [a for a in [v["artist"] for v in self._vessels.values()] if a]

    def assign_artist(self, layer, z_order, color):
        """
        Assigns an artist to a layer based on its geometry type.

        :param layer: The spatial layer for which the artist is being assigned.
        :param z_order: The z-order for rendering the layer.
        :param color: The color for the layer's artist.
        
        :return: The created artist for the layer.
        """
        if isinstance(layer.geometry, MultiLineString):
            artist = []
            for line in layer.geometry.geoms:
                artist.append(self.new_line_artist(line, color, z_order))
        else:
            artist = self.new_artist(layer.geometry, color, z_order=z_order)
        return artist

    def new_artist(self, geometry, color, z_order=None, **kwargs):
        """
        Creates a new artist for a given geometry and adds it to the display.

        :param geometry: The geometry to be rendered.
        :param color: The color of the geometry.
        :param z_order: The z-order for rendering.
        :param kwargs: Additional arguments to be passed to the artist creation.

        :return: The created artist for the geometry.
        """
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
        """
        Creates a new line artist for a given line geometry.

        :param line_geometry: The line geometry to be rendered.
        :param color: The color of the line.
        :param z_order: The z-order for rendering.
        :param kwargs: Additional arguments for line customization.

        :return: The created line artist.
        """
        x, y = line_geometry.xy
        line = self._display.axes.add_line(Line2D(x, y, color=color, linewidth=kwargs.get('linewidth', 0.5)))
        if z_order is None:
            line.set_animated(True)
        else:
            line.set_zorder(z_order)
        return line

    def add_arrow(
        self, start, end, color_name, buffer, fill, head_size, linewidth, linestyle
    ):
        """
        Adds an arrow overlay from a start point to an end point.

        :param start: The starting coordinates of the arrow.
        :param end: The ending coordinates of the arrow.
        :param color_name: The name of the color for the arrow.
        :param buffer: The buffer size for the arrow.
        :param fill: Whether the arrow should be filled.
        :param head_size: The size of the arrow head.
        :param linewidth: The width of the arrow line.
        :param linestyle: The style of the arrow line.

        :return: The created arrow artist.
        """
        if buffer is None:
            buffer = 5
        if head_size is None:
            head_size = 50
        body = shapes.Arrow(start=start, end=end, width=buffer).body(head_size)
        return self.add_overlay(body, color_name, fill, linewidth, linestyle)

    def add_circle(self, center, radius, color_name, fill, linewidth, linestyle, alpha):
        """
        Adds a circle overlay to the display.

        :param center: The center coordinates of the circle.
        :param radius: The radius of the circle.
        :param color_name: The name of the color for the circle.
        :param fill: Whether the circle should be filled.
        :param linewidth: The width of the circle outline.
        :param linestyle: The style of the circle outline.
        :param alpha: The transparency level of the circle.

        :return: The created circle artist.
        """
        geometry = shapes.Circle(*center, radius).geometry
        self.add_overlay(geometry, color_name, fill, linewidth, linestyle, alpha)

    def add_line(self, points, color_name, buffer, linewidth, linestyle, marker):
        """
        Adds a line overlay to the display using a list of points.

        :param points: The list of (x, y) points for the line.
        :param color_name: The name of the color for the line.
        :param buffer: The buffer size for the line.
        :param linewidth: The width of the line.
        :param linestyle: The style of the line.
        :param marker: The marker style for the line.

        :return: The created line artist.
        """
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
        """
        Adds an overlay geometry to the display.

        :param geometry: The geometry to overlay.
        :param color_name: The name of the color for the overlay.
        :param fill: Whether the overlay should be filled.
        :param linewidth: The width of the overlay line.
        :param linestyle: The style of the overlay line.
        :param alpha: The transparency level of the overlay.

        :return: The created overlay artist.
        """
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
        """
        Adds a rectangle overlay to the display.

        :param center: The center coordinates of the rectangle.
        :param size: The width and height of the rectangle.
        :param color_name: The name of the color for the rectangle.
        :param rotation: The rotation angle of the rectangle.
        :param fill: Whether the rectangle should be filled.
        :param linewidth: The width of the rectangle outline.
        :param linestyle: The style of the rectangle outline.
        :param alpha: The transparency of the rectangle.

        :return: The created rectangle artist.
        """
        geometry = shapes.Rectangle(
            *center, heading=rotation, width=size[0], height=size[1]
        ).geometry
        self.add_overlay(geometry, color_name, fill, linewidth, linestyle, alpha)

    def add_overlay(self, geometry, color_name, fill, linewidth, linestyle, alpha=1.0):
        """
        Adds an overlay geometry to the display.

        :param geometry: The geometry to overlay.
        :param color_name: The name of the color for the overlay.
        :param fill: Whether the overlay should be filled.
        :param linewidth: The width of the overlay line.
        :param linestyle: The style of the overlay line.
        :param alpha: The transparency level of the overlay.

        :return: The created overlay artist.
        """
        color = color_picker(color_name)
        if fill is False:
            color = color[0], "none"
        kwargs = {}
        if linewidth is not None:
            kwargs["linewidth"] = linewidth
        if linestyle is not None:
            kwargs["linestyle"] = linestyle
        kwargs["alpha"] = alpha
        return self.new_artist(geometry, color, 0, **kwargs)

    def update_vessels(self):
        """
        Updates the vessels displayed on the plot by reading ship positions 
        from a data source and replacing the existing vessel artists.
        """
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
        """
        Replaces the currently displayed vessel artists with new ones.

        :param new_artists: A dictionary of new vessel artists keyed by their IDs.
        """
        for vessel in self._vessels.values():
            vessel["artist"].remove()
        self._vessels = new_artists

    def toggle_vessels_visibility(self, new_state: bool = None):
        """
        Toggles the visibility of vessel features on the display.

        :param new_state: If provided, sets the visibility state; 
                          otherwise toggles the current state.
        """
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
        """
        Sets the visibility of an artist or a list of artists.

        :param artist: The artist or list of artists to set visibility for.
        :param new_state: The visibility state to set.
        """
        if not isinstance(artist, list):
            artist.set_visible(new_state)
        else:
            for line in artist:
                line.set_visible(new_state)

    def toggle_topography_visibility(self, new_state: bool = None):
        """
        Toggles the visibility of land and shore features.

        :param new_state: If provided, sets the visibility state; 
                          otherwise toggles the current state.
        """
        if new_state is None:
            new_state = not self._land.get_visible()
        self.set_visibility(self._land, new_state)
        self.set_visibility(self._shore, new_state)
        self._display.redraw_plot()

    def show_top_hidden_layer(self):
        """
        Shows the next hidden seabed layer that is above the current top layer.
        """
        artists = self._z_sorted_seabeds(descending=False)
        self._toggle_next_visibility_layer(artists, visibility=True)

    def hide_top_visible_layer(self):
        """
        Hides the topmost visible seabed layer.
        """
        artists = self._z_sorted_seabeds(descending=False)
        self._toggle_next_visibility_layer(artists, visibility=False)

    def hide_bottom_visible_layer(self):
        """
        Hides the bottommost visible seabed layer.
        """
        artists = self._z_sorted_seabeds(descending=True)
        self._toggle_next_visibility_layer(artists, visibility=False)

    def show_bottom_hidden_layer(self):
        """
        Shows the next hidden seabed layer that is below the current bottom layer.
        """
        artists = self._z_sorted_seabeds(descending=True)
        self._toggle_next_visibility_layer(artists, visibility=True)

    def _toggle_next_visibility_layer(self, artists, visibility):
        """
        Toggles the visibility of the next layer in the provided list of artists.

        :param artists: A list of artists representing seabed layers.
        :param visibility: The visibility state to set for the layer.
        """
        if self._any_toggleable_layer(artists, not visibility):
            artist = self._next_visibility_layer(artists, not visibility)
            artist.set_visible(visibility)
            self._display.redraw_plot()

    def _z_sorted_seabeds(self, descending=False):
        """
        Retrieves the seabed artists sorted by their z-order.

        :param descending (bool): If True, sorts in descending order.

        :return: A list of seabed artists sorted by z-order.
        """
        artist_keys = sorted(self._seabeds, reverse=descending)
        return [self._seabeds[key] for key in artist_keys]

    @staticmethod
    def _any_toggleable_layer(artists, visible):
        """
        Checks if any artist in the list has the specified visibility state.

        :param artists: A list of artists to check.
        :param visible: The visibility state to check against.

        :return: True if any artist has the specified visibility state, False otherwise.
        """
        return any([a.get_visible() is visible for a in artists])

    @staticmethod
    def _next_visibility_layer(artists, visibility):
        """
        Finds the next artist in the list with the specified visibility state.

        :param artists: A list of artists to search.
        :param visibility: The visibility state to look for.

        :return: The next artist that matches the specified visibility state.
        """
        return next(a for a in artists if a.get_visible() is visibility)

    @staticmethod
    def vessels_to_file(vessel_poses: list[tuple]) -> None:
        """
        Writes vessel positions to a CSV file.

        :param vessel_poses: A list of tuples containing vessel data to write.
        """
        core.files.write_rows_to_csv(
            [("id", "x", "y", "heading", "color")] + vessel_poses,
            core.paths.vessels,
        )
