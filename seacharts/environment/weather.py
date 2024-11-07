"""
Contains the WeatherData class for containing parsed weather data.
"""
from dataclasses import dataclass

import requests
from dataclasses import dataclass

from seacharts.layers import VirtualWeatherLayer, WeatherLayer
from .collection import DataCollection

time_dict = {
    "hour": 60,
    "day": 60 * 24,
    "week": 60 * 24 * 7,
    "month": None,
    "year": None,
}


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
            if unformatted_data is not None:
                self.parse_data(unformatted_data)

    def verify_scope(self):
        ...

    def fetch_data(self, query_dict) -> dict:
        """
        fetch data from PyThor service
        :param query_dict: Dict with API query data
        :return: Dictionary with weather data.
        """
        api_query = query_dict["PyThor_address"] + "/api/weather?"
        query_dict.pop("PyThor_address")
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
        latitude_start, longitude_start = self.scope.extent.convert_utm_to_lat_lon(x_min, y_min)
        latitude_end, longitude_end = self.scope.extent.convert_utm_to_lat_lon(x_max, y_max)
        api_query += "&latitude_start=" + str(latitude_start - 0.5 if latitude_start - 0.5 >= -90 else -90)
        api_query += "&longitude_start=" + str(longitude_start - 0.5 if longitude_start - 0.5 >= -180 else -180)
        api_query += "&latitude_end=" + str(latitude_end + 0.5 if latitude_end + 0.5 <= 90 else 90)
        api_query += "&longitude_end=" + str(longitude_end + 0.5 if longitude_end + 0.5 <= 180 else 180)
        api_query += "&time_start=" + str(self.scope.time.epoch_times[0]) + "&time_end=" + str(
            self.scope.time.epoch_times[-1] + 3600)
        if time_dict[self.scope.time.period] is not None:
            api_query += "&interval=" + str(int(time_dict[self.scope.time.period] * self.scope.time.period_mult))
        else:
            import warnings
            warnings.warn(
                "Specified time period is not supported by the weather module this may lead to unspecified behaviour. Weather won't be downloaded")
            return None
        print("PyThor request:" + api_query)
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

    def find_by_name(self, name: str) -> VirtualWeatherLayer:
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None

    def get_value(self, name, time, lat, lon):
        lon = 360 + lon if lon < 0 else lon
        from scipy.interpolate import RegularGridInterpolator as rgi
        time_epoch = time.timestamp()
        grid = []
        times = []
        layers = self.find_by_name(name).weather
        layers.sort(key = lambda layer: layer.time)
        for i in range(len(layers)):
            if layers[i].time >= time_epoch and i>0:
                times = [layers[i - 1].time, layers[i].time]
                grid = [layers[i - 1].data, layers[i].data]
                break
        fn = rgi((times,self.latitude,self.longitude), grid)
        return fn((time_epoch,lat,lon))
