from __future__ import annotations

import matplotlib.pyplot as plt

import seacharts.display as dis


class EventsManager:
    _zoom_scale = 0.9

    def __init__(self, display: dis.Display):
        self._display = display
        self._canvas = display.figure.canvas
        self._x_view_limit = None
        self._y_view_limit = None
        self._mouse_press = None
        self._connect_canvas_events()
        self._remove_default_keybindings()

    def _connect_canvas_events(self):
        self._canvas.mpl_connect('scroll_event', self._handle_zoom)
        self._canvas.mpl_connect('key_press_event', self._key_press)
        self._canvas.mpl_connect('button_press_event', self._click_press)
        self._canvas.mpl_connect('button_release_event', self._click_release)
        self._canvas.mpl_connect('motion_notify_event', self._mouse_motion)

    def _handle_zoom(self, event):
        if event.button == 'down':
            scale_factor = 1 / self._zoom_scale
        elif event.button == 'up':
            scale_factor = self._zoom_scale
        else:
            raise NotImplementedError
        x_limit = self._display.axes.get_xlim()
        y_limit = self._display.axes.get_ylim()
        new_width = (x_limit[1] - x_limit[0]) * scale_factor
        new_height = (y_limit[1] - y_limit[0]) * scale_factor
        x_data, y_data = event.xdata, event.ydata
        dx = (x_limit[1] - x_data) / (x_limit[1] - x_limit[0])
        dy = (y_limit[1] - y_data) / (y_limit[1] - y_limit[0])
        self._display.axes.set_xlim(
            [x_data - new_width * (1 - dx), x_data + new_width * dx]
        )
        self._display.axes.set_ylim(
            [y_data - new_height * (1 - dy), y_data + new_height * dy]
        )
        self._display.update_plot()

    def _key_press(self, event):
        if event.key == 'escape':
            self._display.terminate()
        elif event.key == 't':
            self._display.features.show_top_hidden_layer()
        elif event.key == 'g':
            self._display.features.show_bottom_hidden_layer()
        elif event.key == 'h':
            self._display.features.hide_top_visible_layer()
        elif event.key == 'b':
            self._display.features.hide_bottom_visible_layer()
        elif event.key == 'u':
            self._display.features.update()
        elif event.key == 'v':
            self._display.features.toggle_vessels_visibility()
        elif event.key == 'k':
            self._display.features.toggle_shore_visibility()
        elif event.key == 'l':
            self._display.features.toggle_land_visibility()

    def _click_press(self, event):
        if event.inaxes != self._display.axes:
            return
        self._x_view_limit = self._display.axes.get_xlim()
        self._y_view_limit = self._display.axes.get_ylim()
        self._mouse_press = dict(x=event.xdata, y=event.ydata)

    def _click_release(self, _):
        self._mouse_press = None
        self._display.update_plot()

    def _mouse_motion(self, event):
        if self._mouse_press is None:
            return
        if event.inaxes != self._display.axes:
            return
        self._x_view_limit -= (event.xdata - self._mouse_press['x'])
        self._y_view_limit -= (event.ydata - self._mouse_press['y'])
        self._display.axes.set_xlim(self._x_view_limit)
        self._display.axes.set_ylim(self._y_view_limit)
        self._display.update_plot()

    @staticmethod
    def _remove_default_keybindings():
        dic = plt.rcParams
        plt.rcParams['keymap.pan'].remove('p')
        plt.rcParams['keymap.zoom'].remove('o')
        plt.rcParams['keymap.grid'].remove('g')
        plt.rcParams['keymap.save'].remove('s')
        plt.rcParams['keymap.back'].remove('left')
        plt.rcParams['keymap.xscale'].remove('k')
        plt.rcParams['keymap.yscale'].remove('l')
        plt.rcParams['keymap.forward'].remove('v')
        plt.rcParams['keymap.forward'].remove('right')
        plt.rcParams['keymap.all_axes'].remove('a')
