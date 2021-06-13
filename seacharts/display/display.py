from __future__ import annotations

import datetime
import time
from multiprocessing import Process
from tkinter import TclError
from typing import Tuple, List

import matplotlib.pyplot as plt
from cartopy.crs import UTM

import seacharts.data.config as config
import seacharts.environment as env
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
        self._dark_mode = False
        self._background = None
        self.figure = self._init_figure()
        self.axes = self._init_axes()
        self.events = EventsManager(self)
        self.features = FeaturesManager(self)
        self.draw_plot()
        if int(self.settings['dark_mode'][0]):
            self.toggle_dark_mode()
        if environment is None:
            self.start_visualization_loop()

    def _init_figure(self):
        dpi = int(self.settings['dpi'][0])
        resolution = int(self.settings['resolution'][0])
        width, height = self.environment.scope.extent.size
        window_height, ratio = resolution / dpi, width / height
        figure_size = ratio * window_height, window_height
        figure = plt.figure('SeaCharts', figsize=figure_size, dpi=dpi)
        figure.subplots_adjust(left=0, right=1, bottom=0, top=1)
        return figure

    def _init_axes(self):
        axes = self.figure.add_subplot(projection=self.crs)
        x_min, y_min, x_max, y_max = self.environment.scope.extent.bbox
        axes.set_extent((x_min, x_max, y_min, y_max), crs=self.crs)
        axes.background_patch.set_visible(False)
        axes.outline_patch.set_visible(False)
        return axes

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
