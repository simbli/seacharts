from __future__ import annotations

import seacharts.spatial as spl
from .scope import Scope


class Environment:
    def __init__(self, settings: dict):
        self.scope = Scope(settings)
        self.hydrography = spl.Hydrography(self.scope)
        self.topography = spl.Topography(self.scope)
        self.load_existing_shapefiles()

    def load_existing_shapefiles(self):
        self.hydrography.load(self.scope)
        self.topography.load(self.scope)
        if self.hydrography.loaded or self.topography.loaded:
            print("INFO: ENC created using data from existing shapefiles.\n")
        else:
            print("INFO: No existing spatial data was found.")
            self.parse_data_into_shapefiles()

    def parse_data_into_shapefiles(self):
        if not list(self.scope.parser.gdb_paths):
            resources = sorted(list(set(self.scope.resources)))
            if not resources:
                print(
                    "WARNING: No spatial data source location given in config."
                )
            else:
                message = "WARNING: No spatial data sources were located in\n"
                message += "         "
                resources = [f"'{r}'" for r in resources]
                message += ", ".join(resources[:-1])
                if len(resources) > 1:
                    message += f" and {resources[-1]}"
                print(message + ".")
            return
        print(
            "INFO: Updating ENC with data from available resources..."
        )
        self.hydrography.parse(self.scope)
        self.topography.parse(self.scope)
        if self.hydrography.loaded or self.topography.loaded:
            print("\nENC update complete.\n")
        else:
            print("WARNING: Given spatial data source(s) seem empty.\n")
