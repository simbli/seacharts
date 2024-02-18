from seacharts import spatial
from .scope import Scope


class Environment:
    def __init__(self, settings: dict):
        self.scope = Scope(settings)
        self.map = spatial.MapData(self.scope)
        self.user = spatial.UserData(self.scope)
        self.weather = spatial.WeatherData(self.scope)

        self.map.load_existing_shapefiles()
        if not self.map.loaded:
            self.map.parse_resources_into_shapefiles()
