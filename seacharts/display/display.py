from __future__ import annotations

import datetime
import time
import tkinter as tk
from pathlib import Path
from typing import List, Tuple, Union, Any

import matplotlib
import matplotlib.pyplot as plt
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
    crs = UTM(33)
    window_anchors = (
        ("top_left", "top", "top_right"),
        ("left", "center", "right"),
        ("bottom_left", "bottom", "bottom_right"),
    )

    def __init__(self, settings: dict, environment: env.Environment):
        self._settings = settings
        self.environment = environment
        self._show_figure = False
        self._setup_figure_parameters(settings)

    def _setup_figure_parameters(self, settings: dict) -> None:
        if self._show_figure:
            self._background = None
            self.anchor_index = self._init_anchor_index(settings)
            self.figure, self.sizes, self.spacing, widths = self._init_figure(settings)
            self.axes, self.grid_spec, self._colorbar = self._init_axes(widths)
            self.events = EventsManager(self)
            self.features = FeaturesManager(self)
            self.axes.add_artist(
                ScaleBar(
                    1,
                    units="m",
                    location="lower left",
                    frameon=False,
                    color="white",
                    box_alpha=0.0,
                    pad=0.5,
                    font_properties={"size": 12},
                )
            )

            self.draw_plot()

            if self._fullscreen_mode:
                self.toggle_fullscreen()
            else:
                self.set_figure_position()

            # if self._colorbar_mode:
            #     self.toggle_colorbar()

            self.toggle_dark_mode(self._dark_mode)

            if self.environment is None:
                self.start_visualization_loop()

    def start(self) -> None:
        """
        Starts the display, if it is not already started.
        Overrides the show_figure setting if set to false.
        """
        if self.is_active:
            return

        if not self._show_figure:
            self._show_figure = True

        self._setup_figure_parameters(self._settings)
        plt.show(block=False)

    def _init_anchor_index(self, settings):
        option = settings["display"]["anchor"]
        for j, window_anchor in enumerate(self.window_anchors):
            if option in window_anchor:
                return j, window_anchor.index(option)
        raise ValueError(
            f"Invalid window anchor option '{option}', "
            f"possible candidates are: \n"
            f"{[o for options in self.window_anchors for o in options]}"
        )

    def _init_figure(self, settings):
        self._fullscreen_mode = settings["display"]["fullscreen"]
        self._colorbar_mode = settings["display"]["colorbar"]
        self._dark_mode = settings["display"]["dark_mode"]
        self._dpi = settings["display"]["dpi"]
        self._resolution = settings["display"]["resolution"]

        if self._fullscreen_mode:
            plt.rcParams["toolbar"] = "None"

        width, height = self.environment.scope.extent.size
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
        x_min, y_min, x_max, y_max = self.environment.scope.extent.bbox
        axes1.set_extent((x_min, x_max, y_min, y_max), crs=self.crs)
        axes2 = self.figure.add_subplot(gs[0, 1])
        cb = colorbar(axes2, self.environment.scope.depths)
        return axes1, gs, cb

    def start_visualization_loop(self):
        if not self._show_figure:
            return

        print()
        self.show(0.1)
        start_time = time.time()
        while True:
            delta = datetime.timedelta(seconds=time.time() - start_time)
            now = str(delta).split(".")[0]
            print(f"\rVisualizing multiprocessing environment | {now}", end="")
            if not self.is_active:
                self.terminate()
                print()
                return
            self.features.update_vessels()
            self.update_plot()
            time.sleep(0.1)

    def refresh_vessels(self, poses: List[Tuple]):
        if not self._show_figure:
            return

        self.features.vessels_to_file(poses)
        self.features.update_vessels()
        self.update_plot()

    def update_plot(self):
        if not self._show_figure:
            return

        self.figure.canvas.restore_region(self._background)
        self.draw_animated_artists()

    def draw_plot(self):
        if not self._show_figure:
            return
        plt.show(block=False)
        try:
            self.figure.canvas.draw()
        except tk.TclError:
            plt.close()
        self._background = self.figure.canvas.copy_from_bbox(self.figure.bbox)
        self.draw_animated_artists()

    def draw_animated_artists(self):
        if not self._show_figure:
            return

        for artist in self.features.animated:
            self.axes.draw_artist(artist)
        try:
            self.figure.canvas.blit()
            self.figure.canvas.flush_events()
        except tk.TclError:
            plt.close()

    def toggle_dark_mode(self, state=None):
        if not self._show_figure:
            return

        state = state if state is not None else not self._dark_mode
        color = "#142c38" if state else "#ffffff"
        self.figure.set_facecolor(color)
        self.figure.axes[0].set_facecolor(color)
        self._colorbar.ax.set_facecolor(color)
        self.features.toggle_topography_visibility(not state)
        self._dark_mode = state
        self.draw_plot()

    def toggle_colorbar(self, state=None):
        if not self._show_figure:
            return

        if state is not None:
            self._colorbar_mode = state
        else:
            self._colorbar_mode = not self._colorbar_mode
        self.grid_spec.update(**self.spacing[int(self._colorbar_mode)])
        if not self._fullscreen_mode:
            self.figure.set_size_inches(self.sizes[int(self._colorbar_mode)])
            self.set_figure_position()
        self.draw_plot()

    def toggle_fullscreen(self, state=None):
        if not self._show_figure:
            return

        if state is not None:
            self._fullscreen_mode = state
        else:
            self._fullscreen_mode = not self._fullscreen_mode
        plt.get_current_fig_manager().full_screen_toggle()
        if not self._fullscreen_mode:
            self.figure.set_size_inches(self.sizes[int(self._colorbar_mode)])
            self.set_figure_position()
        self.draw_plot()

    def set_figure_position(self):
        if not self._show_figure:
            return

        j, i = self.anchor_index
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
            manager.window.wm_geometry(f"+{x + x_margin}+{y}")

    def save_figure(
        self,
        name: str | None = None,
        path: Path | None = None,
        scale: float = 1.0,
        extension: str = "png",
    ):
        if not self._show_figure:
            return

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
    def is_active(self):
        if not self._show_figure:
            return

        return plt.fignum_exists(self.figure.number)

    def show(self, duration=0.0):
        if not self._show_figure:
            return

        if self.environment.ownship:
            self.features.update_ownship()
            if self.environment.safe_area:
                self.features.update_hazards()
        try:
            plt.pause(duration)
        except tk.TclError:
            plt.close()

    def terminate(self):
        if not self._show_figure:
            return
        plt.close(self.figure)
        self._show_figure = False

    def dark_mode(self, arg: bool = True) -> None:
        """
        Enable or disable dark mode view of environment figure.
        :param arg: boolean switching dark mode on or off
        :return: None
        """
        self.toggle_dark_mode(arg)

    def fullscreen_mode(self, arg: bool = True) -> None:
        """
        Enable or disable fullscreen mode view of environment figure.
        :param arg: boolean switching fullscreen mode on or off
        :return: None
        """
        self.toggle_fullscreen(arg)

    def colorbar(self, arg: bool = True) -> None:
        """
        Enable or disable the colorbar legend of environment figure.
        :param arg: boolean switching the colorbar on or off.
        """
        self.toggle_colorbar(arg)

    def add_vessels(self, *args: Tuple[int, int, int, int, str]) -> None:
        """
        Add colored vessel features to the displayed environment plot.
        :param args: tuples with id, easting, northing, heading, color
        :return: None
        """
        self.refresh_vessels(list(args))

    def clear_vessels(self) -> None:
        """
        Remove all vessel features from the environment plot.
        :return: None
        """
        self.refresh_vessels([])

    def draw_arrow(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        color: str,
        width: float = None,
        fill: bool = False,
        head_size: float = None,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
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
        center: Tuple[float, float],
        radius: float,
        color: str,
        fill: bool = True,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
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
        points: List[Tuple[float, float]],
        color: str,
        width: float = None,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
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
        geometry: Union[Any, List[Tuple[float, float]]],
        color: str,
        interiors: List[List[Tuple[float, float]]] = None,
        fill: bool = True,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
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
        center: Tuple[float, float],
        size: Tuple[float, float],
        color: str,
        rotation: float = 0.0,
        fill: bool = True,
        thickness: float = None,
        edge_style: Union[str, tuple] = None,
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

    def get_handles(self):
        """Returns figure and axes handles to the seacharts display."""
        return self.figure, self.axes

    def refresh(self) -> None:
        """
        Manually redraw the environment display window.
        :return: None
        """
        self.draw_plot()

    def close(self) -> None:
        """
        Close the environment display window and clear all vessels.
        :return: None
        """
        self.terminate()
        self.clear_vessels()

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
        self.save_figure(name, path, scale, extension)
