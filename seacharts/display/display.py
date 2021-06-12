from __future__ import annotations

import datetime
import time
from multiprocessing import Process
from tkinter import TclError
from typing import Tuple, List

import matplotlib.pyplot as plt
from cartopy.crs import UTM

import seacharts.environment as env
from .events import EventsManager
from .features import FeaturesManager


class Display:
    crs = UTM(33)
    figure_size = 18, 12

    def __init__(self, environment: env.Environment = None):
        if environment is not None:
            self.environment = environment
        else:
            self.environment = env.Environment()
        self.figure = plt.figure('SeaCharts', figsize=self.figure_size)
        self.axes = self.figure.add_subplot(projection=self.crs)
        self.background = None
        self._format_hypsometry()
        self.events = EventsManager(self)
        self.features = FeaturesManager(self)
        self.draw_plot()
        if environment is None:
            self.start_visualization_loop()

    def _format_hypsometry(self):
        x_min, y_min, x_max, y_max = self.environment.scope.extent.bbox
        self.axes.set_extent((x_min, x_max, y_min, y_max), crs=self.crs)
        self.axes.background_patch.set_visible(False)
        self.axes.outline_patch.set_visible(False)
        self.figure.subplots_adjust(
            left=0.05, right=0.95, bottom=0.05, top=0.95
        )

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
        self.figure.canvas.restore_region(self.background)
        self.draw_animated_artists()

    def draw_plot(self):
        self.figure.canvas.draw()
        self.background = self.figure.canvas.copy_from_bbox(self.figure.bbox)
        self.draw_animated_artists()

    def draw_animated_artists(self):
        for artist in self.features.animated:
            self.axes.draw_artist(artist)
        self.figure.canvas.blit()
        self.figure.canvas.flush_events()

    def save_figure(self, name=None):
        if name is None:
            name = self.figure.canvas.manager.get_window_title()
        self.figure.savefig(f"reports/{name}.png", dpi=self.figure.dpi,
                            bbox_inches='tight', pad_inches=0.5)

    @property
    def is_active(self):
        return plt.fignum_exists(self.figure.number)

    @staticmethod
    def show(duration=0.0):
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
