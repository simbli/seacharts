"""
Contains attribute-specific subtypes for inheritance usage with the Shape class.
"""
from dataclasses import dataclass


@dataclass
class Coordinates:
    x: float
    y: float


@dataclass
class Vector(Coordinates):
    pass


@dataclass
class Radial:
    radius: float


@dataclass
class Oriented:
    heading: float
    in_degrees: bool = True
