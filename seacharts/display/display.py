from __future__ import annotations

import datetime
import time
from multiprocessing import Process
from tkinter import TclError
from typing import Tuple, List

import matplotlib.pyplot as plt
from cartopy.crs import UTM
from matplotlib.gridspec import GridSpec

import seacharts.data.config as config
import seacharts.environment as env
from .colors import colorbar
from .events import EventsManager
from .features import FeaturesManager


class Display:
    crs = UTM(33)
    settings = config.read_settings('DISPLAY')

    def __init__(self, environment: env.Environment = None):
        if environment is None:
            self.environment = env.Environment()
        else:
            self.environment = environment
        self._colorbar = False
        self._dark_mode = False
        self._background = None
        self.figure, self.sizes, self.spacing, widths = self._init_figure()
        self.axes, self.grid_spec = self._init_axes(widths)
        self.events = EventsManager(self)
        self.features = FeaturesManager(self)
        self.draw_plot()
        if int(self.settings['dark_mode'][0]):
            self.toggle_dark_mode()
        if environment is None:
            self.start_visualization_loop()

    def _init_figure(self):
        if int(self.settings['full_screen'][0]):
            plt.rcParams['toolbar'] = 'None'
        dpi = int(self.settings['dpi'][0])
        resolution = int(self.settings['resolution'][0])
        width, height = self.environment.scope.extent.size
        window_height, ratio = resolution / dpi, width / height
        figure_width1, figure_height1 = ratio * window_height, window_height
        axes1_width, axes2_width, width_space = figure_width1, 1.0, 0.3
        axes_widths = axes1_width, axes2_width
        figure_height2 = figure_height1
        figure_width2 = axes1_width + width_space + 2 * axes2_width
        figure_sizes = [(figure_width1, figure_height1),
                        (figure_width2, figure_height2)]
        sub1 = dict(
            right=(axes1_width + width_space + axes2_width) / figure_width1,
            wspace=2 * width_space / (axes1_width + axes2_width),
        )
        sub2 = dict(
            right=(axes1_width + width_space + axes2_width) / figure_width2,
            wspace=2 * width_space / axes1_width,
        )
        subplot_spacing = sub1, sub2
        figure = plt.figure('SeaCharts', figsize=figure_sizes[0], dpi=dpi)
        if int(self.settings['full_screen'][0]):
            plt.get_current_fig_manager().full_screen_toggle()
        return figure, figure_sizes, subplot_spacing, axes_widths

    def _init_axes(self, axes_widths):
        gs = GridSpec(1, 2, width_ratios=axes_widths, **self.spacing[0],
                      left=0.0, top=1.0, bottom=0.0, hspace=0.0)
        axes1 = self.figure.add_subplot(gs[0, 0], projection=self.crs)
        x_min, y_min, x_max, y_max = self.environment.scope.extent.bbox
        axes1.set_extent((x_min, x_max, y_min, y_max), crs=self.crs)
        axes1.background_patch.set_visible(False)
        axes1.outline_patch.set_visible(False)
        axes2 = self.figure.add_subplot(gs[0, 1])
        colorbar(axes2, self.environment.scope.depths)
        return axes1, gs

    def start_visualization_loop(self):
        print()
        self.show(0.1)
        start_time = time.time()
        while True:
            delta = datetime.timedelta(seconds=time.time() - start_time)
            now = str(delta).split(".")[0]
            print(
                f"\rVisualizing multiprocessing environment | {now}", end=''
            )
            if not self.is_active:
                self.terminate()
                print()
                return
            self.features.update_vessels()
            self.update_plot()
            time.sleep(0.1)

    def refresh_vessels(self, poses: List[Tuple]):
        self.features.vessels_to_file(poses)
        self.features.update_vessels()
        self.update_plot()

    def update_plot(self):
        self.figure.canvas.restore_region(self._background)
        self.draw_animated_artists()

    def draw_plot(self):
        self.figure.canvas.draw()
        self._background = self.figure.canvas.copy_from_bbox(self.figure.bbox)
        self.draw_animated_artists()

    def draw_animated_artists(self):
        for artist in self.features.animated:
            self.axes.draw_artist(artist)
        self.figure.canvas.blit()
        self.figure.canvas.flush_events()

    def toggle_dark_mode(self, state=None):
        state = state if state is not None else not self._dark_mode
        self.figure.set_facecolor('#142c38' if state else '#ffffff')
        self.features.toggle_topography_visibility(not state)
        self._dark_mode = state
        self.draw_plot()

    def toggle_colorbar(self):
        self._colorbar = not self._colorbar
        self.grid_spec.update(**self.spacing[int(self._colorbar)])
        self.figure.set_size_inches(self.sizes[int(self._colorbar)])
        self.draw_plot()

    def save_figure(self, name=None, scale=1.0):
        if name is None:
            name = self.figure.canvas.manager.get_window_title()
        self.figure.savefig(f"reports/{name}.png", dpi=self.figure.dpi * scale,
                            bbox_inches='tight', pad_inches=0.0)

    @property
    def is_active(self):
        return plt.fignum_exists(self.figure.number)

    def show(self, duration=0.0):
        if self.environment.ownship:
            self.features.update_ownship()
            if self.environment.safe_area:
                self.features.update_hazards()
        try:
            plt.pause(duration)
        except TclError:
            plt.close()

    @staticmethod
    def terminate():
        plt.close()

    @staticmethod
    def init_multiprocessing():
        Process(target=Display).start()
