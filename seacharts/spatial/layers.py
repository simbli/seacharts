from __future__ import annotations

from dataclasses import dataclass

from . import base


@dataclass
class Seabed(base.SingleDepthRegions):
    color = 'seabed'
    z_order = -300
    _external_labels = [
        dict(layer='dybdeareal', depth='minimumsdybde'),
        dict(layer='grunne', depth='dybde'),
    ]


@dataclass
class Land(base.ZeroDepthRegions):
    color = 'land'
    z_order = -100
    _external_labels = ['landareal']


@dataclass
class Shore(base.ZeroDepthRegions):
    color = 'shore'
    z_order = -200
    _external_labels = [
        'skjer', 'torrfall', 'landareal', 'ikkekartlagtsjomaltomr'
    ]


supported_layers = [cls.__name__ for cls in [
    Seabed,
    Land,
    Shore,
]]
