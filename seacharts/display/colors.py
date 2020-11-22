import matplotlib.colorbar as clb
import matplotlib.colors as clr
import matplotlib.pyplot as plt
import numpy as np

_reds = plt.get_cmap('Reds')(np.linspace(0.0, 1.0, 9))
_blues = plt.get_cmap('Blues')(np.linspace(0.3, 0.9, 9))
_greens = plt.get_cmap('Greens')(np.linspace(0.0, 1.0, 9))

_standard_colors = {
    'horizon': '#ffffff22',
    'white': '#ffffffaa',
    'red': '#ff4747aa',
    'yellow': '#fff047aa',
    'cyan': '#47ffffaa',
    'orange': '#f59e42aa',
    'purple': '#d078ffaa',
}

legend_colors = {
    'red': ('#ff0000', '#ff000055'),
    'orange': ('#ff9900', '#ff990055'),
    'yellow': ('#ffcc00', '#ffcc0055'),
    'green': ('#00ff00', '#00ff0055'),
    'cyan': ('#00ffff', '#00ffff55'),
    'purple': ('#9900ff', '#9900ff55'),
    'pink': ('#ff00ff', '#ff00ff55'),
    'grey_d': ('#666666', '#66666655'),
    'grey_l': ('#b7b7b7', '#b7b7b755'),
    'white': ('#d9d9d9', '#ffffff55'),
}

_feature_colors = {
    'Seabed': _blues[4],
    'Land': _greens[4],
    'Shore': _greens[3],
    'Rocks': _reds[5],
    'Shallows': _reds[3],
    'Ship': _standard_colors['white'],
    'Patch': _standard_colors['red'],
}


def color(name, depths=None):
    if isinstance(name, int):
        return plt.get_cmap('Blues')(np.linspace(0.3, 0.9, len(depths)))[name]
    if name == 'Ocean':
        if depths is None:
            raise ValueError(
                f"Ocean color map need depth bins"
            )
        else:
            return plt.get_cmap('Blues')(np.linspace(0.3, 0.9, len(depths)))
    elif name in _feature_colors:
        return _feature_colors[name]
    elif name in _standard_colors:
        return _standard_colors[name]
    else:
        raise ValueError(
            f"{name} is not a valid color"
        )


def colorbar(axes, depths):
    depths = list(depths)
    ocean = color('Ocean', depths)
    colors = [_feature_colors['Shore']] + list(ocean)
    cmap = clr.LinearSegmentedColormap.from_list(
        'Custom terrain', colors, len(colors)
    )
    cmap.set_over(plt.get_cmap('Blues')(np.linspace(0.0, 1.0, 9))[-1])
    cmap.set_under(_feature_colors['Land'])
    norm = clr.BoundaryNorm([0, 1] + depths[1:], cmap.N)
    kwargs = dict(cmap=cmap, norm=norm, extend='both',
                  format='%1i m', ticks=[0, 1] + depths[1:],
                  boundaries=([depths[0] - 100] + [0, 1] +
                              depths[1:] + [depths[-1] + 100]))
    clb.ColorbarBase(axes, **kwargs).ax.invert_yaxis()
