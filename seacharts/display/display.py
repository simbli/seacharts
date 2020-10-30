import glob

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from PIL import Image
from cartopy.feature import ShapelyFeature

import seacharts.settings as config
from .colors import color, colorbar


class Display:
    def __init__(self):
        self.scope = config.get_user_scope()
        self.environment = {f.__name__: f() for f in self.scope.features}
        self.figure = plt.figure('Map', figsize=config.figure_size)
        self.grid = self.figure.add_gridspec(*config.grid_size)
        self.colorbar = self.format_colorbar(self.scope.depths)
        self.topography = self.format_topography()
        self.ships = [config.Ship()]
        self.ship_patches = list(self.create_ship_patches())
        for feature in self.environment.values():
            feature.load(self.scope.bounding_box)
        self.draw(self.environment)
        self.background = None
        self.figure.canvas.draw()
        self.figure.canvas.mpl_connect("draw_event", self.on_draw)
        self.figure.canvas.mpl_connect('close_event', self.close)
        plt.ion()
        self.simulate_test_ship()

    @property
    def is_active(self):
        return plt.fignum_exists(self.figure.number)

    def format_topography(self):
        axes = self.figure.add_subplot(self.grid[:, :-1],
                                       projection=config.crs)
        x_min, y_min, x_max, y_max = self.scope.bounding_box
        axes.set_extent((x_min, x_max, y_min, y_max), crs=config.crs)
        axes.set_facecolor(color('Seabed'))
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
            if self.is_active:
                self.figure.canvas.blit()

    def create_ship_patches(self):
        for ship in self.ships:
            clr = color(ship.name)
            patch = patches.Polygon(ship.hull, config.crs, fc=clr, ec=clr)
            self.topography.add_patch(patch)
            yield patch

    def draw(self, environment, lines=False):
        for feature in environment.values():
            if feature.name != 'Seabed':
                face = color(feature.name)
                edge = 'k' if lines else face
                shape = ShapelyFeature(feature.shapely, config.crs,
                                       facecolor=face, edgecolor=edge)
                self.topography.add_feature(shape)

    def simulate_test_ship(self):
        print("Simulating test ship...")
        for j in range(100):
            if not self.is_active:
                self.close()
                return
            self.pause()
            for ship in self.ships:
                ship.update_position(config.fps)
            self.update()
            self.save_frame(j)
        self.close()
        self.save_simulation()

    def save(self, name='map'):
        self.figure.savefig(config.path_frame_files.replace('*', name))

    def save_frame(self, i):
        name = ''.join(['0' for _ in range(3 - len(str(i)))]) + str(i)
        path = config.path_frame_files.replace('*', name)
        self.figure.savefig(path)

    @staticmethod
    def save_simulation():
        print("Creating simulation GIF...")
        fp_in, fp_out = config.path_frame_files, config.path_simulation
        frame1, *frames = [Image.open(f) for f in glob.glob(fp_in)]
        frame1.save(fp=fp_out, format='GIF', append_images=frames,
                    save_all=True, duration=1000 / config.fps, loop=0)
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
