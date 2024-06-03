import requests

class WeatherManager:
    def __init__(self, weatherSettings: dict):
        query_dict = weatherSettings.copy()
        api_query = query_dict["Pythor_adress"] + "/api/weather?"
        query_dict.pop("Pythor_adress")
        for k,v in query_dict.items():
            api_query += k + "="
            if v is not list:
                api_query += str(v)+"&"
            else:
                for weater_var in v:
                    api_query+= str(weater_var) + ","
                api_query = api_query[:-1]+"&"
        api_query = api_query[:-1]
        print(api_query)
        self.unformated_data = requests.get (api_query)
