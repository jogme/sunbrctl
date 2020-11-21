from datetime import datetime, time
import json
import requests

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
    def __init__(self):
        self.update_time()
        self.get_todays_sunrise()

# TODO
# create a function, that returns what stage of the day is it rn
# and what is the % between the current two stages
# consider the refresh rate between different two day stages
