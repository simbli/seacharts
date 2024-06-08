"""
Contains the WeatherData class for containing parsed weather data.
"""
from dataclasses import dataclass

import requests
from dataclasses import dataclass

from seacharts.layers import VirtualWeatherLayer, WeatherLayer
from .collection import DataCollection


@dataclass
class WeatherData(DataCollection):
    longitude: float = None
    latitude: float = None
    time: int = None

    def __post_init__(self):
        print("k")
        self.weather_layers = list()
        if self.scope.weather:
            self.verify_scope()
            unformatted_data = self.fetch_data(self.scope.weather.copy())
            self.parse_data(unformatted_data)

    def verify_scope(self):
        ...

    @staticmethod
    def fetch_data(query_dict) -> dict:
        api_query = query_dict["PyThor_adress"] + "/api/weather?"
        query_dict.pop("PyThor_adress")
        for k, v in query_dict.items():
            api_query += k + "="
            if not isinstance(v, list):
                api_query += str(v) + "&"
            else:
                for weater_var in v:
                    api_query += str(weater_var) + ","
                api_query = api_query[:-1] + "&"
        api_query = api_query[:-1]
        print(api_query)
        return requests.get(api_query).json()

    def parse_data(self, data: dict) -> None:
        self.time = data.pop("time_inter")
        self.latitude = data.pop("lat_inter")
        self.longitude = data.pop("lon_inter")

        for k, v in data.items():
            new_layer = VirtualWeatherLayer(name=k, weather=list())
            for time_index, weather_data in enumerate(v):
                new_layer.weather.append(WeatherLayer(time=self.time[time_index], data=weather_data))
            self.weather_layers.append(new_layer)

    @property
    def layers(self) -> list[VirtualWeatherLayer]:
        return self.weather_layers

    @property
    def loaded(self) -> bool:
        return any(self.layers)
