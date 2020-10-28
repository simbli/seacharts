import os
import pathlib

import matplotlib.pyplot as plt
from cartopy.crs import UTM
from cartopy.feature import ShapelyFeature

from .colors import color, colorbar


class Map:
    crs = UTM(33)
    grid_size = (1, 12)
    window_size = (12, 7)
    path_reports = 'reports'

    def __init__(self, bounding_box, depths):
        self.figure = plt.figure('Map', figsize=self.window_size)
        self.grid = self.figure.add_gridspec(*self.grid_size)
        self.bb = tuple(bounding_box[i] for i in (0, 2, 1, 3))
        self.colorbar = self.format_colorbar(depths)
        self.topography = self.format_topography()

    def format_topography(self):
        axes = self.figure.add_subplot(self.grid[:, :-1], projection=self.crs)
        axes.set_extent(self.bb, crs=self.crs)
        axes.set_facecolor(color('Seabed'))
        return axes

    def format_colorbar(self, depths):
        axes = self.figure.add_subplot(self.grid[:, -1])
        colorbar(axes, depths)
        return axes

    def plot(self, layer):
        geometries = (feature.geometry for feature in layer)
        rgba = color(layer[0].name)
        shape = ShapelyFeature(geometries, self.crs, color=rgba)
        self.topography.add_feature(shape)

    def plot_ship(self, ship):
        geometries = [ship.hull]
        rgba = color('red')
        shape = ShapelyFeature(geometries, self.crs, color=rgba)
        self.topography.add_feature(shape)

    def save(self, name='map'):
        pathlib.Path(self.path_reports).mkdir(parents=True, exist_ok=True)
        self.figure.savefig(os.path.join(self.path_reports, name + '.png'))

    def show(self):
        self.save()
        plt.show()

    @staticmethod
    def wait(interval=0.1):
        plt.waitforbuttonpress(interval)

    @staticmethod
    def close():
        plt.close()
