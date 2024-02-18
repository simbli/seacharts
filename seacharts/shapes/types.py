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
