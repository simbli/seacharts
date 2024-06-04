"""
Contains core classes and functions used throughout the SeaCharts package.
"""
from . import files
from . import paths
from .config import Config
from .parser import DataParser
from .parserFGDB import FGDBParser
from .parserS57 import S57Parser
from .scope import Scope, MapFormat
