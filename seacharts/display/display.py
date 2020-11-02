import matplotlib.pyplot as plt

import seacharts.settings as config


class Display:
    def __init__(self):
        config.remove_past_gif_frames()
        self.scope = config.get_user_scope()
        self.environment = self.scope.environment
        self.figure = plt.figure('Map', figsize=config.figure_size)
        self.grid = self.figure.add_gridspec(*config.grid_size)
        self.colorbar = self.format_colorbar(self.scope.depths)
        self.topography = self.format_topography()
        self.background = self.figure.canvas.copy_from_bbox(self.figure.bbox)
        self.ships = []
        self.artists = []
        self.draw_environment()
        self.init_event_manager()
        self.init_visualization_loop()

    @property
    def is_active(self):
        return plt.fignum_exists(self.figure.number)

    def format_topography(self):
        ax = self.figure.add_subplot(self.grid[:, :-1], projection=config.crs)
        x_min, y_min, x_max, y_max = self.scope.bounding_box
        ax.set_extent((x_min, x_max, y_min, y_max), crs=config.crs)
        ax.set_facecolor(config.color('Seabed'))
        return ax

    def format_colorbar(self, depths):
        axes = self.figure.add_subplot(self.grid[:, -1])
        config.colorbar(axes, depths)
        return axes

    def init_event_manager(self):
        self.figure.canvas.draw()
        self.figure.canvas.mpl_connect('key_press_event', self.handle_key)
        self.figure.canvas.mpl_connect('close_event', self.close)
        plt.ion()

    def handle_key(self, event):
        if event.key == 'escape':
            self.close()

    def update_plot(self):
        poses = config.read_ship_poses()
        if poses is not None:
            self.figure.canvas.restore_region(self.background)
            for i in range(max(len(poses), len(self.artists))):
                if i < len(poses):
                    ship = poses[i]
                    if i >= len(self.ships):
                        artist = self.topography.add_feature(ship)
                        self.artists.append(artist)
                        self.ships.append(ship)
                    self.ships[i].update_pose(ship)
                    self.artists[i].set_visible(True)
                else:
                    self.artists[i].set_visible(False)
            if self.is_active:
                self.figure.canvas.draw()

    def draw_environment(self):
        for feature in self.environment:
            if feature.name != 'Seabed':
                feature.load(self.scope.bounding_box)
                self.topography.add_feature(feature)

    def init_visualization_loop(self):
        count = 0
        while True:
            if not self.is_active:
                self.close()
                return
            self.pause()
            self.update_plot()
            self.save_frame(count)
            count += 1

    def save(self, name='map'):
        self.figure.savefig(config.path_frame_files.replace('*', name))

    def save_frame(self, i):
        name = ''.join(['0' for _ in range(5 - len(str(i)))]) + str(i)
        path = config.path_frame_files.replace('*', name)
        self.figure.savefig(path)

    def show(self):
        self.save()
        plt.show()

    @staticmethod
    def pause(time=1E-9):
        plt.pause(time)

    @staticmethod
    def close():
        plt.close()
