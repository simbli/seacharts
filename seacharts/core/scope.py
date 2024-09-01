"""
Contains the Extent class for defining details related to files of spatial data.
"""
from dataclasses import dataclass
from seacharts.core import files
from .extent import Extent
from .mapFormat import MapFormat
from .time import Time


@dataclass
class Scope:

    def __init__(self, settings: dict):
        self.extent = Extent(settings)
        self.settings = settings
        self.resources = settings["enc"].get("resources", [])
        
        default_depths = [0, 1, 2, 5, 10, 20, 50, 100, 200, 350, 500]
        self.depths = settings["enc"].get("depths", default_depths)
        self.features = ["land", "shore"]
        for depth in self.depths:
            self.features.append(f"seabed{depth}m")

        if settings["enc"].get("S57_layers", []):
            self.type = MapFormat.S57

        else:
            self.type = MapFormat.FGDB

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
        self.weather = settings["enc"].get("weather", [])

        self.extra_layers:dict[str,str] = settings["enc"].get("S57_layers", {})
        self.features.extend(self.extra_layers)


