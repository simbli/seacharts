"""
Contains the Display class for displaying and plotting maritime spatial data.
"""
import tkinter as tk
from pathlib import Path
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.widgets import Slider, RadioButtons
from cartopy.crs import UTM
from matplotlib.gridspec import GridSpec
from matplotlib_scalebar.scalebar import ScaleBar

import seacharts.environment as env
from .colors import colorbar
from .events import EventsManager
from .features import FeaturesManager

matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42
matplotlib.use("TkAgg")


class Display:
    window_anchors = (
        ("top_left", "top", "top_right"),
        ("left", "center", "right"),
        ("bottom_left", "bottom", "bottom_right"),
    )

    def __init__(self, settings: dict, environment: env.Environment):
        self._settings = settings
        self.crs = UTM(environment.scope.extent.utm_zone,
                       southern_hemisphere=environment.scope.extent.southern_hemisphere)

        self._bbox = (max(environment.scope.extent.bbox[0], self.crs.x_limits[0]),  # x-min
                      max(environment.scope.extent.bbox[1], self.crs.y_limits[0]),  # y-min
                      min(environment.scope.extent.bbox[2], self.crs.x_limits[1]),  # x-max
                      min(environment.scope.extent.bbox[3], self.crs.y_limits[1]))  # y-max
        self._environment = environment
        self._background = None
        self._dark_mode = False
        self._colorbar_mode = False
        self._fullscreen_mode = False
        self._controls = True
        self._resolution = 720
        self._dpi = 96
        self._anchor_index = self._init_anchor_index(settings)
        self.figure, self.sizes, self.spacing, w = self._init_figure(settings)
        self.axes, self.grid_spec, self._colorbar = self._init_axes(w)
        self.events = EventsManager(self)
        self.features = FeaturesManager(self)
        self._toggle_colorbar(self._colorbar_mode)
        self._toggle_dark_mode(self._dark_mode)
        self._add_scalebar()
        self.add_control_panel(self._controls)
        self.redraw_plot()
        if self._fullscreen_mode:
            self._toggle_fullscreen(self._fullscreen_mode)
        else:
            self._set_figure_position()

    def start(self) -> None:
        self.started__ = """
        Starts the display, if it is not already started.
        """
        if self._is_active:
            return
        plt.show(block=False)

    @staticmethod
    def show(duration: float = 0.0):
        """
        Show the display for a duration (0 = indefinitely)
        """
        try:
            plt.show(block=False)
            plt.pause(duration)
        except tk.TclError:
            plt.close()

    def dark_mode(self, arg: bool = True) -> None:
        """
        Enable or disable dark mode view of environment figure.
        :param arg: boolean switching dark mode on or off
        :return: None
        """
        self._toggle_dark_mode(arg)

    def fullscreen(self, arg: bool = True) -> None:
        """
        Enable or disable fullscreen mode view of environment figure.
        :param arg: boolean switching fullscreen mode on or off
        :return: None
        """
        self._toggle_fullscreen(arg)

    def colorbar(self, arg: bool = True) -> None:
        """
        Enable or disable the colorbar legend of environment figure.
        :param arg: boolean switching the colorbar on or off.
        """
        self._toggle_colorbar(arg)

    def add_vessels(self, *args: tuple[int, int, int, int, str]) -> None:
        """
        Add colored vessel features to the displayed environment plot.
        :param args: tuples with id, x-coordinate, y-coordinate, heading, color
        :return: None
        """
        self._refresh_vessels(list(args))

    def clear_vessels(self) -> None:
        """
        Remove all vessel features from the environment plot.
        :return: None
        """
        self._refresh_vessels([])

    @staticmethod
    def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100) -> colors.LinearSegmentedColormap:
        """
        helper function to truncate a colormap
        """
        new_cmap = colors.LinearSegmentedColormap.from_list(
            'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
            cmap(np.linspace(minval, maxval, n)))
        return new_cmap

    def draw_weather(self, variable_name):
        ...

    def _draw_arrow_map(self):
        ...

    def _draw_weather_heatmap(self, variable_name: str, cmap: colors.Colormap, label_colour: str) -> None:
        """
        Draws a heatmap and colorbar for specified weather variable using provided color map and label colour for color bar
        :return: None
        """
        weather_layer = self._environment.weather.find_by_name(variable_name)
        if weather_layer is None:
            return
        heatmap_data = weather_layer.weather[self._environment.weather.selected_time_index].data
        x_min, y_min, x_max, y_max = self._environment.scope.extent.bbox
        extent = (x_min, x_max, y_min, y_max)
        ticks = np.linspace(np.nanmin(np.array(heatmap_data)), np.nanmax(np.array(heatmap_data)), num=8)
        self.weather_map = self.axes.imshow(heatmap_data, extent=extent, origin='lower', cmap=cmap, alpha=0.5)
        self._cbar = self.figure.colorbar(self.weather_map, ax=self.axes, shrink=0.7)
        self._cbar.ax.yaxis.set_tick_params(color=label_colour)
        self._cbar.outline.set_edgecolor(label_colour)
        print(heatmap_data)
        print(np.nanmin(np.array(heatmap_data)))
        print(np.nanmax(np.array(heatmap_data)))
        plt.setp(plt.getp(self._cbar.ax.axes, 'yticklabels'), color=label_colour)

    def draw_arrow(
            self,
            start: tuple[float, float],
            end: tuple[float, float],
            color: str,
            width: float = None,
            fill: bool = False,
            head_size: float = None,
            thickness: float = None,
            edge_style: str | tuple = None,
    ) -> None:
        """
        Add a straight arrow overlay to the environment plot.
        :param start: tuple of start point coordinate pair
        :param end: tuple of end point coordinate pair
        :param color: str of line color
        :param width: float denoting the line buffer width
        :param fill: bool which toggles the interior arrow color on/off
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param head_size: float of head size (length) in meters
        :return: None
        """
        self.features.add_arrow(
            start, end, color, width, fill, head_size, thickness, edge_style
        )

    def draw_circle(
            self,
            center: tuple[float, float],
            radius: float,
            color: str,
            fill: bool = True,
            thickness: float = None,
            edge_style: str | tuple = None,
            alpha: float = 1.0,
    ) -> None:
        """
        Add a circle or disk overlay to the environment plot.
        :param center: tuple of circle center coordinates
        :param radius: float of circle radius
        :param color: str of circle color
        :param fill: bool which toggles the interior disk color
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param alpha: float denoting the Matplotlib alpha value
        :return: None
        """
        self.features.add_circle(
            center, radius, color, fill, thickness, edge_style, alpha
        )

    def draw_line(
            self,
            points: list[tuple[float, float]],
            color: str,
            width: float = None,
            thickness: float = None,
            edge_style: str | tuple = None,
            marker_type: str = None,
    ) -> None:
        """
        Add a straight line overlay to the environment plot.
        :param points: list of tuples of coordinate pairs
        :param color: str of line color
        :param width: float denoting the line buffer width
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param marker_type: str denoting the Matplotlib marker type
        :return: None
        """
        self.features.add_line(points, color, width, thickness, edge_style, marker_type)

    def draw_polygon(
            self,
            geometry: Any | list[tuple[float, float]],
            color: str,
            interiors: list[list[tuple[float, float]]] = None,
            fill: bool = True,
            thickness: float = None,
            edge_style: str | tuple = None,
            alpha: float = 1.0,
    ) -> None:
        """
        Add an arbitrary polygon shape overlay to the environment plot.
        :param geometry: Shapely geometry or list of exterior coordinates
        :param interiors: list of lists of interior polygon coordinates
        :param color: str of rectangle color
        :param fill: bool which toggles the interior shape color
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param alpha: float denoting the Matplotlib alpha value
        :return: None
        """
        self.features.add_polygon(
            geometry, color, interiors, fill, thickness, edge_style, alpha
        )

    def draw_rectangle(
            self,
            center: tuple[float, float],
            size: tuple[float, float],
            color: str,
            rotation: float = 0.0,
            fill: bool = True,
            thickness: float = None,
            edge_style: str | tuple = None,
            alpha: float = 1.0,
    ) -> None:
        """
        Add a rectangle or box overlay to the environment plot.
        :param center: tuple of rectangle center coordinates
        :param size: tuple of rectangle (width, height)
        :param color: str of rectangle color
        :param rotation: float denoting the rectangle rotation in degrees
        :param fill: bool which toggles the interior rectangle color
        :param thickness: float denoting the Matplotlib linewidth
        :param edge_style: str or tuple denoting the Matplotlib linestyle
        :param alpha: float denoting the Matplotlib alpha value
        :return: None
        """
        self.features.add_rectangle(
            center, size, color, rotation, fill, thickness, edge_style, alpha
        )

    def save_image(
            self,
            name: str = None,
            path: Path | None = None,
            scale: float = 1.0,
            extension: str = "png",
    ) -> None:
        """
        Save the environment plot as a .png image.
        :param name: optional str of file name
        :param path: optional Path of file path
        :param scale: optional float scaling the image resolution
        :param extension: optional str of file extension name
        :return: None
        """
        self._save_figure(name, path, scale, extension)

    def close(self) -> None:
        """
        Close the environment display window and clear all vessels.
        :return: None
        """
        self._terminate()
        self.clear_vessels()

    def redraw_plot(self):
        """
        Redraw the full environment plot as well as animated artists
        """
        plt.show(block=False)
        try:
            self.figure.canvas.draw()
        except tk.TclError:
            plt.close()
        self._draw_animated_artists()

    def update_plot(self):
        """
        Update only the animated artists of the plot
        """
        self._draw_animated_artists()

    def _init_anchor_index(self, settings):
        option = "center"
        if "display" in settings:
            option = settings["display"].get("anchor", option)
        for j, window_anchor in enumerate(self.window_anchors):
            if option in window_anchor:
                return j, window_anchor.index(option)
        raise ValueError(
            f"Invalid window anchor option '{option}', "
            f"possible candidates are: \n"
            f"{[o for options in self.window_anchors for o in options]}"
        )

    def _init_figure(self, settings):
        if "display" in settings:
            d = settings["display"]
            if "colorbar" in d:
                self._colorbar_mode = d["colorbar"]
            if "dark_mode" in d:
                self._dark_mode = d["dark_mode"]
            if "fullscreen" in d:
                self._fullscreen_mode = d["fullscreen"]
            if "resolution" in d:
                self._resolution = d["resolution"]
            if "dpi" in d:
                self._dpi = d["dpi"]
            if "controls" in d:
                self._controls = d["controls"]

        if self._fullscreen_mode:
            plt.rcParams["toolbar"] = "None"

        width, height = self._environment.scope.extent.size
        window_height, ratio = self._resolution / self._dpi, width / height
        figure_width1, figure_height1 = ratio * window_height, window_height
        axes1_width, axes2_width, width_space = figure_width1, 1.1, 0.3
        axes_widths = axes1_width, axes2_width
        figure_height2 = figure_height1 * 0.998
        figure_width2 = axes1_width + width_space + 2 * axes2_width
        figure_sizes = [
            (figure_width1, figure_height1),
            (figure_width2, figure_height2),
        ]
        sub1 = dict(
            right=(axes1_width + width_space + axes2_width) / figure_width1,
            wspace=2 * width_space / (axes1_width + axes2_width),
        )
        sub2 = dict(
            right=(axes1_width + width_space + axes2_width) / figure_width2,
            wspace=2 * width_space / axes1_width,
        )
        subplot_spacing = sub1, sub2
        figure = plt.figure("SeaCharts", figsize=figure_sizes[0], dpi=self._dpi)
        return figure, figure_sizes, subplot_spacing, axes_widths

    def _init_axes(self, axes_widths):
        gs = GridSpec(
            1,
            2,
            width_ratios=axes_widths,
            **self.spacing[0],
            left=0.0,
            top=1.0,
            bottom=0.0,
            hspace=0.0,
        )
        axes1 = self.figure.add_subplot(gs[0, 0], projection=self.crs)
        x_min, y_min, x_max, y_max = self._environment.scope.extent.bbox
        axes1.set_extent((x_min, x_max, y_min, y_max), crs=self.crs)
        axes2 = self.figure.add_subplot(gs[0, 1])
        cb = colorbar(axes2, self._environment.scope.depths)
        return axes1, gs, cb

    def _add_scalebar(self):
        self.axes.add_artist(
            ScaleBar(
                1,
                units="m",
                location="lower left",
                frameon=False,
                color="white",
                box_alpha=0.0,
                pad=0.5,
                font_properties={"size": 12}
            )
        )

    def _refresh_vessels(self, poses: list[tuple]):
        self.features.vessels_to_file(poses)
        self.features.update_vessels()
        self.update_plot()

    def _draw_animated_artists(self):
        for artist in self.features.animated:
            self.axes.draw_artist(artist)
        try:
            self.figure.canvas.blit()
            self.figure.canvas.flush_events()
        except tk.TclError:
            plt.close()

    def _set_figure_position(self):
        j, i = self._anchor_index
        option = self.window_anchors[j][i]
        if option != "default":
            root = tk.Tk()
            screen_width = int(root.winfo_screenwidth())
            screen_height = int(root.winfo_screenheight())
            root.destroy()
            x_margin, y_margin = -10, -73
            dpi = self._dpi
            size = self.sizes[int(self._colorbar_mode)]
            width, height = [int(size[k] * dpi) for k in range(2)]
            x_shifted = screen_width - width
            y_shifted = screen_height - height
            if option == "center":
                x, y = x_shifted // 2, y_shifted // 2
            elif option == "right":
                x, y = x_shifted, y_shifted // 2
            elif option == "left":
                x, y = 4, y_shifted // 2
            elif option == "top":
                x, y = x_shifted // 2, 2
            elif option == "bottom":
                x, y = x_shifted // 2, y_shifted + y_margin
            elif option == "top_right":
                x, y = x_shifted, 2
            elif option == "top_left":
                x, y = 4, 2
            elif option == "bottom_right":
                x, y = x_shifted, y_shifted + y_margin
            elif option == "bottom_left":
                x, y = 4, y_shifted + y_margin
            else:
                x, y = 4, 2
            manager = plt.get_current_fig_manager()
            # noinspection PyUnresolvedReferences
            manager.window.wm_geometry(f"+{x + x_margin}+{y}")

    def _toggle_dark_mode(self, state=None):
        state = state if state is not None else not self._dark_mode
        color = "#142c38" if state else "#ffffff"
        self.figure.set_facecolor(color)
        self.figure.axes[0].set_facecolor(color)
        self._colorbar.ax.set_facecolor(color)
        self.features.toggle_topography_visibility(not state)
        self._dark_mode = state
        self.redraw_plot()

    def _toggle_colorbar(self, state=None):
        if state is not None:
            self._colorbar_mode = state
        else:
            self._colorbar_mode = not self._colorbar_mode
        self.grid_spec.update(**self.spacing[int(self._colorbar_mode)])
        if not self._fullscreen_mode:
            self.figure.set_size_inches(self.sizes[int(self._colorbar_mode)])
            self._set_figure_position()
        self.redraw_plot()

    def _toggle_fullscreen(self, state=None):
        if state is not None:
            self._fullscreen_mode = state
        else:
            self._fullscreen_mode = not self._fullscreen_mode
        plt.get_current_fig_manager().full_screen_toggle()
        if not self._fullscreen_mode:
            self.figure.set_size_inches(self.sizes[int(self._colorbar_mode)])
            self._set_figure_position()
        self.redraw_plot()

    def get_handles(self):
        """Returns figure and axes handles to the seacharts display."""
        return self.figure, self.axes

    def _save_figure(
            self,
            name: str | None = None,
            path: Path | None = None,
            scale: float = 1.0,
            extension: str = "png",
    ):
        try:
            if name is None:
                name = self.figure.canvas.manager.get_window_title()
            if path is None:
                path_str = f"reports/{name}.{extension}"
            else:
                path_str = str(path / f"{name}.{extension}")
            self.figure.savefig(
                path_str,
                dpi=self.figure.dpi * scale,
                bbox_inches=self.figure.bbox_inches,
                pad_inches=0.0,
            )
        except tk.TclError:
            plt.close()

    @property
    def _is_active(self):
        # noinspection PyUnresolvedReferences
        return plt.fignum_exists(self.figure.number)

    def _terminate(self):
        plt.close(self.figure)

    def _weather_slider_handle(self,val):
        self._environment.weather.selected_time_index = val
        self._cbar.remove()
        self.weather_map.remove()
        self.draw_weather_heatmap(self._environment.weather.weather_layers[0].name,
                                  cmap=self.truncate_colormap(plt.get_cmap('jet'), 0.35, 0.9),
                                  label_colour='white')
        self.redraw_plot()

    def _add_time_slider(self, ax_slider, fig):
        times = self._environment.scope.time.get_datetimes_strings()
        self.slider = Slider(ax=ax_slider, valmin=0, valmax=len(times) - 1, valinit=0, valstep=1, label="Time")
        self.time_label = ax_slider.text(0.5, 1.2, times[0], transform=ax_slider.transAxes,
                        ha='center', va='center', fontsize=12)
        last_value = self.slider.val

        def __on_slider_change(event):
            nonlocal last_value
            if event.button == 1 and event.inaxes == ax_slider:
                val = self.slider.val
                if val != last_value:
                    self._weather_slider_handle(val)
                    last_value = val

        def __update(val):
            index = int(self.slider.val)
            self.time_label.set_text(times[index])
            fig.canvas.draw_idle()

        fig.canvas.mpl_connect('button_release_event', __on_slider_change)
        self.slider.on_changed(__update)
            

    def add_control_panel(self, controls: bool):
        if not controls: return
        fig, (ax_slider, ax_radio) = plt.subplots(2, 1, figsize=(8, 2), gridspec_kw={'height_ratios': [1, 2]})
        if self._environment.scope.time is not None:
            self._add_time_slider(ax_slider=ax_slider, fig=fig)
        
        # VISIBLE LAYER PICKER START
            # if weather layers is not None -> add_radio_pick for weather layers
        radio_labels = ['a', 'b', 'c']
        self.radio_buttons = RadioButtons(ax_radio, ['--'] + radio_labels, active=0)
        def on_radio_change(label):
            print(f"Radio button selected: {label}")
            # Add handling code for radio button change here
        self.radio_buttons.on_clicked(on_radio_change)
        # VISIBLE LAYER PICKER END
        
        # TODO: layer picked in such way should be saved to variable
        # then we can add, analogically to date slider, opacity slider for picked weather layer
        
        # Set the window title and show the figure
        fig.canvas.manager.set_window_title('Controls')
        plt.show()

