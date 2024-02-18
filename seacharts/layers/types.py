"""
Contains attribute-specific subtypes for inheritance usage with the Layer class.
"""
from dataclasses import dataclass


@dataclass
class ZeroDepth:
    depth = 0


@dataclass
class SingleDepth:
    depth: int


@dataclass
class MultiDepth:
    @property
    def depth(self) -> None:
        raise AttributeError("Multi-depth shapes have no single depth.")
