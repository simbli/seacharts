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
    longitude: list[float] = None
    latitude: list[float] = None
    time: list[float] = None
    selected_time_index: int = None

    def __post_init__(self):
        self.weather_names = list()
        self.weather_layers = list()
        if self.scope.weather:
            self.verify_scope()
            unformatted_data = self.fetch_data(self.scope.weather.copy())
            self.parse_data(unformatted_data)

    def verify_scope(self):
        ...

    def fetch_data(self,query_dict) -> dict:
        """
        fetch data from PyThor service
        :param query_dict: Dict with API query data
        :return: Dictionary with weather data.
        """
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
        x_min, y_min, x_max, y_max = self.scope.extent.bbox
        latitude_start,longitude_start = self.scope.extent.convert_utm_to_lat_lon(x_min,y_min)
        latitude_end, longitude_end = self.scope.extent.convert_utm_to_lat_lon(x_max, y_max)
        print(latitude_start,longitude_start,latitude_end, longitude_end)
        api_query += "&latitude_start="+str(latitude_start)
        api_query += "&longitude_start=" + str(longitude_start)
        api_query += "&latitude_end=" + str(latitude_end)
        api_query += "&longitude_end=" + str(longitude_end)
        print(api_query)
        return requests.get(api_query).json()

    def parse_data(self, data: dict) -> None:
        """
        parse data from weather service
        :param data: Dict with data from weather service
        """
        self.time = data.pop("time_inter")
        self.latitude = data.pop("lat_inter")
        self.longitude = data.pop("lon_inter")
        self.selected_time_index = 0
        for k, v in data.items():
            self.weather_names.append(k)
            new_layer = VirtualWeatherLayer(name=k, weather=list())
            for time_index, weather_data in enumerate(v):
                new_layer.weather.append(WeatherLayer(time=self.time[time_index], data=weather_data))
            self.weather_layers.append(new_layer)

    @property
    def layers(self) -> list[VirtualWeatherLayer]:
        return self.weather_layers

    def find_by_name(self,name:str) -> VirtualWeatherLayer:
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None
