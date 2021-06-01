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
        self.events = EventsManager(self)
        self.features = FeaturesManager(self)
        self._format_hypsometry()
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
        start_time = time.time()
        print()
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
            self.show(0.8)
            self.features.update()

    def update_vessels(self, poses: List[Tuple]):
        self.features.vessels_to_file(poses)
        self.features.update()

    def update_plot(self):
        if self.is_active:
            self.figure.canvas.draw()
        else:
            self.terminate()

    def show(self, duration=None):
        try:
            if duration:
                self.pause(duration)
            else:
                plt.show()
        except TclError:
            plt.close()

    def save_figure(self, name=None):
        if name is None:
            name = self.figure.canvas.manager.get_window_title()
        self.figure.savefig(f"reports/{name}.png", dpi=self.figure.dpi,
                            bbox_inches='tight', pad_inches=0.5)

    @property
    def is_active(self):
        return plt.fignum_exists(self.figure.number)

    @staticmethod
    def pause(interval=0.05):
        plt.pause(interval)

    @staticmethod
    def terminate():
        plt.close()

    @staticmethod
    def init_multiprocessing():
        display = Process(target=Display)
        display.start()
        return display
