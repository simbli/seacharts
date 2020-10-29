import glob
import os
import pathlib

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image
from cartopy.crs import UTM
from cartopy.feature import ShapelyFeature

from seacharts.features import Seabed, Land, Shore, Ship
from .colors import color, colorbar


class Display:
    fps = 24
    crs = UTM(33)
    grid_size = (1, 12)
    window_size = (12, 7)
    path_reports = 'reports'
    path_frames = path_reports, 'frames'
    environment = {f.__name__.lower(): f() for f in (Seabed, Land, Shore)}
    default_depths = [0, 3, 6, 10, 20, 50, 100, 200, 300, 400, 500]
    default_region = 'Møre og Romsdal'
    default_origin = (42600, 6956400)
    default_extent = (3000, 2000)

    tr_corner = (i + j for i, j in zip(default_origin, default_extent))
    bounding_box = *default_origin, *tr_corner

    def __init__(self):
        self.figure = plt.figure('Map', figsize=self.window_size)
        self.grid = self.figure.add_gridspec(*self.grid_size)
        self.colorbar = self.format_colorbar(self.default_depths)
        self.topography = self.format_topography()
        self.ships = [Ship()]
        self.ship_patches = list(self.create_ship_patches())
        for feature in self.environment.values():
            feature.load(self.bounding_box)
        self.draw(self.environment)
        self.background = None
        self.figure.canvas.draw()
        self.figure.canvas.mpl_connect("draw_event", self.on_draw)
        plt.ion()
        self.simulate_test_ship()

    def format_topography(self):
        axes = self.figure.add_subplot(self.grid[:, :-1], projection=self.crs)
        bb = tuple(self.bounding_box[i] for i in (0, 2, 1, 3))
        axes.set_extent(bb, crs=self.crs)
        axes.set_facecolor(color('seabed'))
        return axes

    def format_colorbar(self, depths):
        axes = self.figure.add_subplot(self.grid[:, -1])
        colorbar(axes, depths)
        return axes

    def on_draw(self, _):
        self.background = self.figure.canvas.copy_from_bbox(self.figure.bbox)
        for patch in self.ship_patches:
            self.figure.draw_artist(patch)

    def update(self):
        self.figure.canvas.restore_region(self.background)
        for ship, patch in zip(self.ships, self.ship_patches):
            patch.set_xy(ship.hull)
            self.figure.draw_artist(patch)
        self.figure.canvas.blit()

    def create_ship_patches(self):
        for ship in self.ships:
            clr = color(ship.label)
            patch = patches.Polygon(ship.hull, self.crs, fc=clr, ec=clr)
            self.topography.add_patch(patch)
            yield patch

    def draw(self, environment, lines=False):
        for feature in environment.values():
            if feature.name != 'Seabed':
                face = color(feature.label)
                edge = 'k' if lines else face
                shape = ShapelyFeature(feature.shapely, self.crs,
                                       facecolor=face, edgecolor=edge)
                self.topography.add_feature(shape)

    def simulate_test_ship(self):
        print("Simulating test ship...")
        for j in range(100):
            self.pause()
            for ship in self.ships:
                ship.update_position(self.fps)
            self.update()
            self.save_frame(j)
        self.close()
        self.save_simulation()

    def save(self, name='map'):
        pathlib.Path(self.path_reports).mkdir(parents=True, exist_ok=True)
        self.figure.savefig(os.path.join(self.path_reports, name + '.png'))

    def save_frame(self, i):
        name = ''.join(['0' for _ in range(3 - len(str(i)))]) + str(i)
        path = os.path.join(*self.path_frames, 'frame_' + name + '.png')
        pathlib.Path(*self.path_frames).mkdir(parents=True, exist_ok=True)
        self.figure.savefig(path)

    def save_simulation(self):
        print("Creating simulation GIF...")
        fp_in = os.path.join(*self.path_frames, 'frame_*.png')
        fp_out = os.path.join(self.path_reports, 'simulation.gif')
        first_frame, *frames = [Image.open(f) for f in glob.glob(fp_in)]
        first_frame.save(fp=fp_out, format='GIF', append_images=frames,
                         save_all=True, duration=1000 / self.fps, loop=0)
        print("Done.")

    def show(self):
        self.save()
        plt.show()

    @staticmethod
    def pause(time=1E-9):
        plt.pause(time)

    @staticmethod
    def close():
        plt.close()
