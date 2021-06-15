import matplotlib.colorbar as clb
import matplotlib.colors as clr
import matplotlib.pyplot as plt
import numpy as np


def _blues(bins=9):
    # noinspection PyUnresolvedReferences
    return plt.get_cmap('Blues')(np.linspace(0.6, 0.9, bins))


def _greens(bins=9):
    # noinspection PyUnresolvedReferences
    return plt.get_cmap('Greens')(np.linspace(0.3, 0.9, bins))


_ship_colors = dict(
    red=('#ff0000', '#ff000055'),
    orange=('#ff9900', '#ff990055'),
    yellow=('#ffcc00', '#ffcc0055'),
    green=('#00ff00', '#00ff0055'),
    cyan=('#00ffff', '#00ffff55'),
    purple=('#b055ff', '#b055ff55'),
    pink=('#ff77ff', '#ff77ff55'),
    darkgrey=('#666666', '#66666655'),
    lightgrey=('#b7b7b7', '#b7b7b755'),
    white=('#d9d9d9', '#ffffff77'),
)

_horizon_colors = dict(
    full_horizon=('#ffffff55', '#ffffff11'),
    starboard_bow=('#00ff0099', '#00ff0055'),
    starboard_side=('#33ff3399', '#33ff3355'),
    starboard_aft=('#ccffcc99', '#ccffcc55'),
    rear_aft=('#eeeeee99', '#eeeeee55'),
    port_aft=('#ffcccc99', '#ffcccc55'),
    port_side=('#ff333388', '#ff333355'),
    port_bow=('#ff000066', '#ff000055'),
)

_layer_colors = dict(
    seabed=_blues()[4],
    land=_greens()[4],
    shore=_greens()[3],
)


def color_picker(name, bins=None):
    if isinstance(name, int):
        return _blues(bins)[name]
    elif name in _ship_colors:
        return _ship_colors[name]
    elif name in _horizon_colors:
        return _horizon_colors[name]
    elif name in _layer_colors:
        return _layer_colors[name]
    elif name in clr.CSS4_COLORS:
        return clr.CSS4_COLORS[name]
    else:
        raise ValueError(
            f"{name} is not a valid color"
        )


def colorbar(axes, depths):
    depths = list(depths)
    ocean = color_picker('Ocean', len(depths))
    colors = [_layer_colors['Shore']] + list(ocean)
    c_map = clr.LinearSegmentedColormap.from_list(
        'Custom terrain', colors, len(colors)
    )
    c_map.set_over(_blues()[-1])
    c_map.set_under(_layer_colors['Land'])
    norm = clr.BoundaryNorm([0, 1] + depths[1:], c_map.N)
    kwargs = dict(cmap=c_map, norm=norm, extend='both',
                  format='%1i m', ticks=[0, 1] + depths[1:],
                  boundaries=([depths[0] - 100] + [0, 1] +
                              depths[1:] + [depths[-1] + 100]))
    clb.ColorbarBase(axes, **kwargs).ax.invert_yaxis()
