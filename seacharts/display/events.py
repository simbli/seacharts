"""
Contains the EventsManager class for managing display interaction events.
"""
from typing import Any

import matplotlib.pyplot as plt


# noinspection PyProtectedMember
class EventsManager:
    """
    The EventsManager class is responsible for handling various user interaction events 
    within a Matplotlib display. It manages zooming, panning, and keyboard shortcuts 
    for controlling the display of data. This class captures events such as mouse scrolls, 
    key presses, and mouse clicks, enabling users to manipulate the visualization 
    dynamically.

    Attributes:
        _zoom_scale (float): A factor by which to scale the zoom operation.
        _directions (dict): A mapping of direction keys to their corresponding numeric values 
                            for movement (up, down, left, right).
        _display (object): The display object that this EventsManager interacts with.
        _canvas (object): The canvas from the display where the events are connected.
        _view_limits (dict): A dictionary storing the current view limits for x and y axes.
        _direction_keys (dict): A dictionary tracking the state of direction keys.
        _control_pressed (bool): A flag indicating if the control key is currently pressed.
        _shift_pressed (bool): A flag indicating if the shift key is currently pressed.
        _mouse_press (dict): A dictionary storing the mouse press event coordinates.
    """
    _zoom_scale = 0.9
    _directions = {"up": 1, "down": -1, "left": -1, "right": 1}

    def __init__(self, display):
        """
        Initializes the EventsManager with a specified display object.

        :param display: The display object that will be managed by this EventsManager.
        """
        self._display = display
        self._canvas = display.figure.canvas
        self._view_limits = dict(x=None, y=None)
        self._direction_keys = {d: False for d in self._directions}
        self._control_pressed = False
        self._shift_pressed = False
        self._mouse_press = None
        self._connect_canvas_events()

    def _connect_canvas_events(self) -> None:
        """
        Connects various event handlers to the canvas for mouse and keyboard events.
        """
        self._canvas.mpl_connect("scroll_event", self._handle_zoom)
        self._canvas.mpl_connect("key_press_event", self._key_press)
        self._canvas.mpl_connect("key_release_event", self._key_release)
        self._canvas.mpl_connect("button_press_event", self._click_press)
        self._canvas.mpl_connect("button_release_event", self._click_release)
        self._canvas.mpl_connect("motion_notify_event", self._mouse_motion)

    def _handle_zoom(self, event: Any) -> None:
        """
        Handles mouse scroll events to zoom in or out on the display.

        :param event: The scroll event containing the scroll direction and coordinates.
        """
        if event.button == "down":
            scale_factor = 1 / self._zoom_scale
        elif event.button == "up":
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
        self._display.redraw_plot()

    def _key_press(self, event: Any) -> None:
        """
        Handles keyboard press events to trigger various actions such as toggling visibility, 
        saving figures, or moving the display.

        :param event: The key press event containing the key that was pressed.
        """
        if event.key == "escape":
            self._display._terminate()

        elif event.key == "d":
            self._display._toggle_dark_mode()

        elif event.key == "t":
            self._display.features.show_top_hidden_layer()

        elif event.key == "g":
            self._display.features.show_bottom_hidden_layer()

        elif event.key == "h":
            self._display.features.hide_top_visible_layer()

        elif event.key == "b":
            self._display.features.hide_bottom_visible_layer()

        elif event.key == "u":
            self._display.features.update_vessels()
            self._display.update_plot()

        elif event.key == "v":
            self._display.features.toggle_vessels_visibility()

        elif event.key == "p": # there were some issues with 'l' key
            self._display.features.toggle_topography_visibility()

        elif event.key == "c":
            self._display._toggle_colorbar()

        elif event.key == "ctrl+s":
            self._display._save_figure("svg", extension="svg")

        elif event.key == "s":
            self._display._save_figure("low_res", scale=2.0)

        elif event.key == "S":
            self._display._save_figure("high_res", scale=10.0)

        elif event.key == "shift":
            self._shift_pressed = True

        elif event.key == "control":
            self._control_pressed = True

        elif event.key[:4] == "alt+":
            key = event.key[4:]
            if key in self._directions:
                self._move_figure_position(key)

    def _key_release(self, event: Any) -> None:
        """
        Handles keyboard release events, updating the state of direction 
        and modifier keys.

        :param event: The key release event containing the key that was released.
        """
        if event.key in self._directions:
            self._direction_keys[event.key] = False
        elif event.key == "shift":
            self._shift_pressed = False
        elif event.key == "control":
            self._control_pressed = False

    def _move_figure_position(self, key: str) -> None:
        """
        Moves the display figure based on the arrow key pressed.

        :param key: The direction key pressed ('left', 'right', 'up', 'down').
        """
        matrix = self._display.window_anchors
        j, i = self._display._anchor_index
        if key == "left" or key == "right":
            i = (i + self._directions[key]) % len(matrix[0])
        elif key == "up" or key == "down":
            j = (j - self._directions[key]) % len(matrix)
        self._display._anchor_index = j, i
        self._display._set_figure_position()

    def _click_press(self, event: Any) -> None:
        """
        Captures the mouse press event and stores the current view limits.

        :param event: The mouse button press event containing the coordinates.
        """
        if event.inaxes != self._display.axes:
            return
        if event.button == plt.MouseButton.LEFT:
            self._view_limits["x"] = self._display.axes.get_xlim()
            self._view_limits["y"] = self._display.axes.get_ylim()
            self._mouse_press = dict(x=event.xdata, y=event.ydata)

    def _click_release(self, _) -> None:
        """
        Resets mouse press tracking and refreshes the display.
        """
        self._mouse_press = None
        self._display.redraw_plot()

    def _mouse_motion(self, event: Any) -> None:
        """
        Handles mouse movement events to enable panning of the display.

        :param event: The mouse motion event containing the current coordinates.
        """
        if self._mouse_press is None:
            return
        if event.inaxes != self._display.axes:
            return
        self._view_limits["x"] -= event.xdata - self._mouse_press["x"]
        self._view_limits["y"] -= event.ydata - self._mouse_press["y"]
        self._display.axes.set_xlim(self._view_limits["x"])
        self._display.axes.set_ylim(self._view_limits["y"])
        self._display.redraw_plot()
