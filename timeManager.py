from datetime import datetime, time
import json
import requests
import math
from time import sleep

import config

class TimeManager:
    theMediator = None
    current_time = time(0,0,0)
    current_day = datetime.now().day

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

    enable_hooks = [False, False]
    hook_morning_time = None
    hook_evening_time = None
    hook_morning_do = True
    hook_evening_do = True

    no_internet = False
    
    def __init__(self, mediator, enable_hooks):
        self.theMediator = mediator
        self.enable_hooks = enable_hooks
        self.get_todays_sunrise()
        try:
            if not config.morning_on_startup:
                self.hook_morning_do = False
        except NameError:
            pass
        self.update_time()
    def update_time(self):
        d = datetime.now()
        new_time = d.time()

        if d.day != self.current_day:
            #midnight
            self.get_todays_sunrise()
            self.hook_morning_do = True
            self.hook_evening_do = True
            self.current_day = d.day

        if self.enable_hooks[0] and self.hook_morning_do and new_time > self.hook_morning_time and new_time < self.hook_evening_time:
            self.theMediator.notify(self, 'h_m')
            self.hook_morning_do = False
        elif self.enable_hooks[1] and self.hook_evening_do and (new_time > self.hook_evening_time or new_time < self.hook_morning_time):
            self.theMediator.notify(self, 'h_e')
            self.hook_evening_do = False

        self.current_time = new_time
    def get_todays_sunrise(self):
        #using https://sunrise-sunset.org/api
        api_time_format = "%I:%M:%S %p"

        try:
            r = requests.get("https://api.sunrise-sunset.org/json?lat={}&lng={}&date=today".format(config.lat, config.lng))
            if(r.status_code != 200):
                return r.status_code
            self.no_internet = False
        except (requests.ConnectionError, requests.Timeout) as exception:
            self.no_internet = True

        if self.no_internet:
            try:
                with open("latest.data", "r") as f:
                    res_j = json.load(f)['results']
            except:
                while True:
                    try:
                        r = requests.get("https://api.sunrise-sunset.org/json?lat={}&lng={}&date=today".format(config.lat, config.lng))
                        if(r.status_code != 200):
                            return r.status_code
                        self.no_internet = False
                        break
                    except (requests.ConnectionError, requests.Timeout) as exception:
                        sleep(10)
            print('no internet is present')

        if not self.no_internet:
            with open("latest.data", "w+") as f:
                json.dump(r.json(), f)
                print('new data written to file')
            print('internet is here')
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

        if self.enable_hooks[0] == 'civil':
            self.hook_morning_time = self.civil_twilight_begin
        elif self.enable_hooks[0] == 'nautical':
            self.hook_morning_time = self.nautical_twilight_begin
        elif self.enable_hooks[0] == 'astronomical':
            self.hook_morning_time = self.astronomical_twilight_begin

        if self.enable_hooks[1] == 'civil':
            self.hook_evening_time = self.civil_twilight_end
        elif self.enable_hooks[1] == 'nautical':
            self.hook_evening_time = self.nautical_twilight_end
        elif self.enable_hooks[1] == 'astronomical':
            self.hook_evening_time = self.astronomical_twilight_end

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
        if self.no_internet:
            print('trying to get new data')
            self.get_todays_sunrise()
        self.update_time()
        now = self.get_seconds(self.current_time)
        x = self.convert_to_normal_function_interval(self.get_seconds(self.astronomical_twilight_begin),
                self.get_seconds(self.astronomical_twilight_end), 0, 6, now)
        return self._normal_function(x)
