import matplotlib.colors as clr
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.cm import ScalarMappable


def _blues(bins=9):
    # noinspection PyUnresolvedReferences
    return plt.get_cmap('Blues')(np.linspace(0.6, 1.0, bins))


def _greens(bins=9):
    # noinspection PyUnresolvedReferences
    return plt.get_cmap('Greens')(np.linspace(0.3, 0.9, bins))


_ship_colors = dict(
    red=('#ff0000', '#ff000055'),
    blue=('#0000ff', '#0000ff55'),
    green=('#00ff00', '#00ff0055'),
    yellow=('#ffff00', '#ffff0055'),
    cyan=('#00ffff', '#00ffff55'),
    magenta=('#ff00ff', '#ff00ff55'),
    pink=('#ff88ff', '#ff88ff55'),
    purple=('#bb22ff', '#bb22ff55'),
    orange=('#ff9900', '#ff990055'),
    white=('#ffffff', '#ffffff77'),
    lightgrey=('#b7b7b7', '#b7b7b755'),
    grey=('#666666', '#66666655'),
    darkgrey=('#333333', '#33333355'),
    black=('#000000', '#00000077'),
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
    seabed=_blues()[0],
    land=_greens()[4],
    shore=_greens()[3],
    highlight=('#ffffff44', '#ffffff44'),
    blank=('#ffffffff', '#ffffffff'),
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
    ocean = list(_blues(len(depths)))
    colors = [_layer_colors['shore']] + ocean[:-1]
    c_map = clr.LinearSegmentedColormap.from_list(
        'Custom terrain', colors, len(colors)
    )
    c_map.set_over(ocean[-1])
    c_map.set_under(_layer_colors['land'])
    norm = clr.BoundaryNorm([0, 1] + depths[1:], c_map.N)
    kwargs = dict(extend='both', use_gridspec=True, extendfrac=0.1,
                  format='%1i m', ticks=[0, 1] + depths[1:],
                  boundaries=([depths[0] - 100] + [0, 1] +
                              depths[1:] + [depths[-1] + 100]))
    mappable = ScalarMappable(norm=norm, cmap=c_map)
    cb = plt.colorbar(mappable, cax=axes, **kwargs)
    cb.ax.tick_params(labelsize=20, length=5, width=1.5)
    cb.outline.set_linewidth(1.5)
    cb.ax.invert_yaxis()
    return cb
