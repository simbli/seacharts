"""
Contains attribute-specific subtypes for inheritance usage with the Layer class.
"""
from dataclasses import dataclass


@dataclass
class ZeroDepth:
    """Class for layers that exist at zero depth."""
    depth = 0


@dataclass
class SingleDepth:
    """Class for layers that exist at a single specified depth."""
    depth: int


@dataclass
class MultiDepth:
    """Class for layers that can exist at multiple depths."""
    @property
    def depth(self) -> None:
        raise AttributeError("Multi-depth shapes have no single depth.")
