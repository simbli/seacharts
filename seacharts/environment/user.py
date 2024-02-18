"""
Contains the UserData class for containing user-specified spatial data.
"""
from seacharts.layers import Layer
from .collection import DataCollection


class UserData(DataCollection):
    def __post_init__(self):
        self.shapes = {}

    @property
    def layers(self) -> list[Layer]:
        return list(self.shapes.values())
