import matplotlib.colorbar as clb
import matplotlib.colors as clr
import matplotlib.pyplot as plt
import numpy as np

# noinspection PyUnresolvedReferences
_reds = plt.get_cmap('Reds')(np.linspace(0.0, 1.0, 9))
# noinspection PyUnresolvedReferences
_blues = plt.get_cmap('Blues')(np.linspace(0.3, 0.9, 9))
# noinspection PyUnresolvedReferences
_greens = plt.get_cmap('Greens')(np.linspace(0.0, 1.0, 9))

_ship_colors = {
    'red': ('#ff0000', '#ff000055'),
    'orange': ('#ff9900', '#ff990055'),
    'yellow': ('#ffcc00', '#ffcc0055'),
    'green': ('#00ff00', '#00ff0055'),
    'cyan': ('#00ffff', '#00ffff55'),
    'purple': ('#9900ff', '#9900ff55'),
    'pink': ('#ff00ff', '#ff00ff55'),
    'darkgrey': ('#666666', '#66666655'),
    'lightgrey': ('#b7b7b7', '#b7b7b755'),
    'white': ('#d9d9d9', '#ffffff77'),
}

_layer_colors = {
    'seabed': _blues[4],
    'land': _greens[4],
    'shore': _greens[3],
}


def color_picker(name, bins=None):
    if isinstance(name, int):
        # noinspection PyUnresolvedReferences
        return plt.get_cmap('Blues')(np.linspace(0.3, 0.9, bins))[name]
    elif name == 'Ocean':
        if bins is None:
            raise ValueError(
                f"Ocean color map need depth bins"
            )
        else:
            # noinspection PyUnresolvedReferences
            return plt.get_cmap('Blues')(np.linspace(0.3, 0.9, len(bins)))
    elif name in _ship_colors:
        return _ship_colors[name]
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
    cmap = clr.LinearSegmentedColormap.from_list(
        'Custom terrain', colors, len(colors)
    )
    # noinspection PyUnresolvedReferences
    cmap.set_over(plt.get_cmap('Blues')(np.linspace(0.0, 1.0, 9))[-1])
    cmap.set_under(_layer_colors['Land'])
    norm = clr.BoundaryNorm([0, 1] + depths[1:], cmap.N)
    kwargs = dict(cmap=cmap, norm=norm, extend='both',
                  format='%1i m', ticks=[0, 1] + depths[1:],
                  boundaries=([depths[0] - 100] + [0, 1] +
                              depths[1:] + [depths[-1] + 100]))
    clb.ColorbarBase(axes, **kwargs).ax.invert_yaxis()
