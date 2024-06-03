import requests


class WeatherManager:
    def __init__(self, weatherSettings: dict):
        self.unformatted_data = self.fetch_data(weatherSettings.copy())

    @staticmethod
    def fetch_data(query_dict):
        api_query = query_dict["Pythor_adress"] + "/api/weather?"
        query_dict.pop("Pythor_adress")
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
        return requests.get(api_query)
