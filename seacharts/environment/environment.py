from seacharts.spatial import SpatialData
from .scope import Scope


class Environment:
    def __init__(self, settings: dict):
        self.scope = Scope(settings)
        self.data = SpatialData(self.scope)
        self.data.load_existing_shapefiles()
        if not self.data.loaded:
            self.data.parse_resources_into_shapefiles()
