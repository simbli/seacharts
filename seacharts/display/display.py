from __future__ import annotations

import datetime
import time
import tkinter as tk
from multiprocessing import Process
from pathlib import Path
from typing import List, Tuple

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


class Display:
    crs = None
    window_anchors = (
        ("top_left", "top", "top_right"),
        ("left", "center", "right"),
        ("bottom_left", "bottom", "bottom_right"),
    )

    def __init__(self, settings: dict, environment: env.Environment):
        self.environment = environment
        self._show_figure = settings["display"]["show_figure"]
        self._utm_zone = settings["enc"]["utm_zone"]
        self._setup_figure_parameters(settings)

    def _setup_figure_parameters(self, settings: dict) -> None:
        if self._show_figure:
            self.crs = UTM(settings["enc"]["utm_zone"])
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

    def start(self, settings: dict) -> None:
        """Starts the display, if it is not already started.
        Overrides the show_figure setting if set to false.

        Args:
            settings (dict): The ENC settings dictionary.
        """
        if self.is_active:
            return

        if not self._show_figure:
            self._show_figure = True

        self._setup_figure_parameters(settings)
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
        self._fullscreen_mode = settings["display"]["fullscreen_mode"]
        self._colorbar_mode = settings["display"]["colorbar_mode"]
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
    def utm_zone(self):
        return self._utm_zone

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

    @staticmethod
    def init_multiprocessing():
        Process(target=Display).start()
