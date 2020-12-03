from datetime import datetime, time
import json
import requests
import math

import config

class TimeManager:
    current_time = datetime.now().time()

    sunrise = None
    noon = None
    sunset = None
    day_length = None
    civil_twilight_begin = None
    civil_twilight_end = None
    nautical_twilight_begin = None
    nautical_twilight_end = None
    astronomical_twilight_begin = None
    astronomical_twilight_end = None
    
    def __init__(self):
        self.update_time()
        self.get_todays_sunrise()
    def update_time(self):
        self.current_time = datetime.now().time()
    def get_todays_sunrise(self):
        #using https://sunrise-sunset.org/api
        api_time_format = "%I:%M:%S %p"

        r = requests.get("https://api.sunrise-sunset.org/json?lat={}&lng={}&date=today".format(config.lat, config.lng))
        if(r.status_code != 200):
            return -1

        res_j = r.json()['results']

        self.sunrise = datetime.strptime(res_j['sunrise'], api_time_format).time()
        self.sunset = datetime.strptime(res_j['sunset'], api_time_format).time()
        self.noon = datetime.strptime(res_j['solar_noon'], api_time_format).time()
        self.day_length = datetime.strptime(res_j['day_length'], "%H:%M:%S").time()
        self.civil_twilight_begin = datetime.strptime(res_j['civil_twilight_begin'], api_time_format).time()
        self.civil_twilight_end = datetime.strptime(res_j['civil_twilight_end'], api_time_format).time()
        self.nautical_twilight_begin = datetime.strptime(res_j['nautical_twilight_begin'], api_time_format).time()
        self.nautical_twilight_end = datetime.strptime(res_j['nautical_twilight_end'], api_time_format).time()
        self.astronomical_twilight_begin = datetime.strptime(res_j['astronomical_twilight_begin'], api_time_format).time()
        self.astronomical_twilight_end = datetime.strptime(res_j['astronomical_twilight_end'], api_time_format).time()

    def get_seconds(self, time):
        return ((time.hour*60)+time.minute)*60+time.second

    #domain: the function gives non-zero output on the interval of <0.2,5.7>
    #the center is at 3
    def _normal_function(self, x):
        return int(((1/(0.35*math.sqrt(2*math.pi)))**((-(x-3)**6)/2**4))*100)

    #<a,b> is the input interval
    #<c,d> is the output interval
    #x is the number to be converted
    def convert_to_normal_function_interval(self, a, b, c, d, x):
        if a == b:
            raise
        return c+((d-c)/(b-a))*(x-a)

    def get_current_br(self):
        self.update_time()
        now = self.get_seconds(self.current_time)
        x = self.convert_to_normal_function_interval(self.get_seconds(self.astronomical_twilight_begin),
                self.get_seconds(self.astronomical_twilight_end), 0.2, 5.7, now)
        return self._normal_function(x)
