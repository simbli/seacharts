"""
Contains the Scope class for defining the extent, layers, depth bins, and other 
settings for spatial data files in Electronic Navigational Charts (ENC).
"""
from dataclasses import dataclass
from seacharts.core import files
from .extent import Extent
from .mapFormat import MapFormat
from .time import Time


@dataclass
class Scope:
    """
    Scope class to configure spatial data settings, including the geographic extent, 
    resources, depth layers, map format, and optional temporal configuration. 
    It parses ENC configuration details and prepares features for use.

    :param settings: A dictionary containing configuration settings for ENC.
    """
    def __init__(self, settings: dict):
        """
        Initializes the Scope instance based on settings provided in the configuration dictionary.

        :param settings: Dictionary of ENC configuration settings, including resources, 
                         depths, time configuration, and layer format information.
        """
        self.extent = Extent(settings)
        self.settings = settings
        self.resources = settings["enc"].get("resources", [])
        
        # Set default depth bins if not provided in settings
        default_depths = [0, 1, 2, 5, 10, 20, 50, 100, 200, 350, 500]
        self.depths = settings["enc"].get("depths", default_depths)

        # Define core features for ENC, adding "seabed" layers based on depth bins
        self.features = ["land", "shore"]
        for depth in self.depths:
            self.features.append(f"seabed{depth}m")

        # Set map format type based on provided layer information (S57 or FGDB)
        if settings["enc"].get("S57_layers", []):
            self.type = MapFormat.S57
        else:
            self.type = MapFormat.FGDB

        # Configure temporal settings if specified in configuration
        time_config = settings["enc"].get("time", {})
        if time_config:
            self.time = Time(
                time_start=time_config["time_start"],
                time_end=time_config["time_end"],
                period=time_config["period"],
                period_mult=time_config["period_multiplier"]
            )
        else:
            self.time = None

        # Set weather data sources and any extra S57 layers
        self.weather = settings["enc"].get("weather", [])
        self.extra_layers:dict[str,str] = settings["enc"].get("S57_layers", {})
        # Extend features to include any extra layers specified
        self.features.extend(self.extra_layers)


