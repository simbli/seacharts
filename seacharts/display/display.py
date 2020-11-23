from tkinter import TclError

import matplotlib.pyplot as plt

from .. import settings as config


class Display:
    def __init__(self, independent=True):
        self.ships = []
        self.artists = []
        self.scope = config.get_user_scope()
        self.environment = self.scope.environment
        self.figure = plt.figure('Map', figsize=config.figure_size)
        self.figure.subplots_adjust(left=0, right=1.04, bottom=0.02, top=0.98)
        self.topography = self.format_topography()
        self.background = self.copy_canvas()
        self.draw_environment_features()
        self.init_event_manager()
        self.add_colorbar()
        if independent:
            self.visualization_loop()
        else:
            self.add_legends()

    @property
    def is_active(self):
        return plt.fignum_exists(self.figure.number)

    def format_topography(self):
        axes = self.figure.add_subplot(projection=config.crs)
        x_min, y_min, x_max, y_max = self.scope.bounding_box
        axes.set_extent((x_min, x_max, y_min, y_max), crs=config.crs)
        axes.set_facecolor(config.color('Seabed'))
        return axes

    def add_colorbar(self):
        box = self.topography.get_position()
        axes = self.figure.add_axes([box.x1 + 0.03, box.y0, 0.05, box.height])
        config.colorbar(axes, self.scope.depths)

    def add_legends(self):
        width, height = 6, 30
        box = self.topography.get_position()
        axes = self.figure.add_axes([box.x0 - 0.17, box.y0, 0.17, box.height])
        colors = config.legend_colors.values()
        labels = config.legend_labels
        axes.set_aspect('equal')
        axes.set_ylim(0, height)
        axes.set_xlim(0, width)
        axes.axis('off')
        padding = height / len(colors)
        start = height - (height - (len(colors) - 1) * padding) / 2
        for i, (color, label) in enumerate(zip(colors, labels)):
            ec, fc = color
            h = start - i * padding
            axes.add_artist(plt.Circle(
                (width * 0.9, h), 0.4, edgecolor=ec, facecolor=fc, linewidth=1
            ))
            axes.text(
                width * 0.7, h, label,
                verticalalignment='center', horizontalalignment='right'
            )

    def copy_canvas(self):
        return self.figure.canvas.copy_from_bbox(self.figure.bbox)

    def draw_environment_features(self):
        for feature in self.environment:
            feature.load(self.scope.bounding_box)
            if feature.name == 'Seabed':
                for f in feature.split_ocean_depths(self.scope.depths):
                    self.topography.add_feature(f)
            else:
                self.topography.add_feature(feature)

    def init_event_manager(self):
        self.figure.canvas.draw()
        self.figure.canvas.mpl_connect('key_press_event', self.handle_key)
        self.figure.canvas.mpl_connect('close_event', self.close)
        plt.ion()

    def handle_key(self, event):
        if event.key == 'escape':
            self.close()

    def visualization_loop(self):
        config.remove_past_gif_frames()
        count = 0
        while True:
            if not self.is_active:
                self.close()
                return
            self.pause()
            self.update_plot(count)
            count += 1

    def update_plot(self, k):
        poses = config.read_ship_poses()
        if poses is not None and (len(poses) + len(self.artists)) > 0:
            self.figure.canvas.restore_region(self.background)
            for i in range(max(len(poses), len(self.artists))):
                if i < len(poses):
                    pose = tuple(poses[i])
                    if len(pose) > 3:
                        color_index = int(pose[3])
                        ec, fc = config.ship_colors[color_index]
                        kwargs = dict(ec=ec, fc=fc, zorder=1000 - color_index)
                    else:
                        kwargs = {}
                    ship = config.Ship(*pose[:3], self.scope.origin, **kwargs)
                    if i >= len(self.ships):
                        artist = self.topography.add_feature(ship)
                        self.artists.append(artist)
                        self.ships.append(ship)
                    self.ships[i].update_pose(ship)
                    self.artists[i].set_visible(True)
                else:
                    self.artists[i].set_visible(False)
            if self.is_active:
                self.figure.canvas.blit()
                self.save_frame(k)

    def save(self, name='map'):
        self.figure.savefig(config.path_frame_files.replace('*', name),
                            bbox_inches='tight')

    def save_frame(self, i):
        name = ''.join(['0' for _ in range(5 - len(str(i)))]) + str(i)
        path = str(config.path_frame_files).replace('*', name)
        self.figure.savefig(path)

    def show(self):
        self.save()
        plt.show()

    @staticmethod
    def wait():
        plt.waitforbuttonpress()

    @staticmethod
    def pause(interval=0.05):
        try:
            plt.pause(interval)
        except TclError:
            plt.close()

    @staticmethod
    def close():
        plt.close()
