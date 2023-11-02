"""
Module containing the supported feature layers, which currently only include
labels found in the FGDB distributed by the Norwegian Mapping Authority.
"""
from dataclasses import dataclass

from . import base


@dataclass
class Seabed(base.SingleDepthRegions):
    color = "seabed"
    z_order = -300
    _external_labels = [
        dict(layer="dybdeareal", depth="minimumsdybde"),
        dict(layer="grunne", depth="dybde"),
    ]


@dataclass
class Land(base.ZeroDepthRegions):
    color = "land"
    z_order = -100
    _external_labels = ["landareal"]


@dataclass
class Shore(base.ZeroDepthRegions):
    color = "shore"
    z_order = -200
    _external_labels = ["skjer", "torrfall", "landareal", "ikkekartlagtsjomaltomr"]
