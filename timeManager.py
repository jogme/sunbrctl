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
    minB = 0
    maxB = 100
    
    def __init__(self, mediator, enable_hooks):
        self.theMediator = mediator
        self.enable_hooks = enable_hooks
        self.get_todays_sunrise()
        try:
            if not config.morning_on_startup:
                self.hook_morning_do = False
        except NameError:
            pass
        self.update_time('first')
    def update_time(self, order=None):
        d = datetime.now()
        new_time = d.time()

        if d.day != self.current_day:
            #midnight
            self.get_todays_sunrise()
            self.hook_morning_do = True
            self.hook_evening_do = True
            self.current_day = d.day
            sleep(self.get_seconds(self.astronomical_twilight_being))

        # FIXME
        # there is an issue with non-DST as then the api returns some different times
        # this works nice in summertime (DST)
        self.theMediator.debug("update_time: new_time: " + new_time.strftime("%H:%M:%S"))
        self.theMediator.debug("update_time: evening hook time: " + self.hook_evening_time.strftime("%H:%M:%S"))
        self.theMediator.debug("update_time: morning hook time: " + self.hook_morning_time.strftime("%H:%M:%S"))
        if self.enable_hooks[0] and self.hook_morning_do and new_time > self.hook_morning_time and new_time < self.hook_evening_time:
            self.theMediator.notify(self, 'h_m')
            self.hook_morning_do = False
        elif self.enable_hooks[1] and self.hook_evening_do and (new_time > self.hook_evening_time or new_time < self.hook_morning_time):
            self.theMediator.notify(self, 'h_e')
            self.hook_evening_do = False
        if not order and new_time > self.astronomical_twilight_end:
            #86400s is a day + 60s to go past midnight
            self.theMediator.debug('update_time: going to sleep. Good night!')
            sleep((self.get_seconds(self.astronomical_twilight_end)-86460)*-1)

        self.current_time = new_time
    def get_todays_sunrise(self):
        #using https://sunrise-sunset.org/api
        api_time_format = "%I:%M:%S %p"
        self.theMediator.debug('get_todays_sunrise: getting todays sunrise data')

        try:
            self.theMediator.debug("get_todays_sunrise: https://api.sunrise-sunset.org/json?lat={}&lng={}&date=today".format(config.lat, config.lng))
            r = requests.get("https://api.sunrise-sunset.org/json?lat={}&lng={}&date=today".format(config.lat, config.lng))
            if(r.status_code != 200):
                return r.status_code
            #self.no_internet = False
        except (requests.ConnectionError, requests.Timeout) as exception:
            self.no_internet = True

        if self.no_internet:
            self.theMediator.debug('get_todays_sunrise: no internet connection')
            try:
                with open("latest.data", "r") as f:
                    res_j = json.load(f)['results']
                    self.theMediator.debug('get_todays_sunrise: opened old sunrise data file')
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

        else:
            with open("latest.data", "w") as f:
                json.dump(r.json(), f)
                self.theMediator.debug('get_todays_sunrise: written new sunrise data to the file')
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
    def _normal_function(self, x, minB, maxB):
        minB /= 100
        maxB /= 100
        base = 1/(0.35*math.sqrt(2*math.pi))
        return int((base**(((-(x-3)**6)/(2**4))+math.log(maxB-minB, base))+minB)*100)
    #domain: the function gives non-zero output on the interval of <0,8>
    #the center is at 4
    def _normal_function_evening(self, x):
        base = 1/(0.35*math.sqrt(2*math.pi))
        return int(((1/(0.35*math.sqrt(2*math.pi)))**((-(x-4)**4)/2**3))*100)

    #<a,b> is the input interval
    #<c,d> is the output interval
    #x is the number to be converted
    def convert_to_normal_function_interval(self, a, b, c, d, x):
        if a == b:
            raise
        return c+((d-c)/(b-a))*(x-a)

    def get_current_br(self, order=None):
        #if not self.no_internet:
        #    self.get_todays_sunrise()
        self.update_time(order)
        now = self.get_seconds(self.current_time)
        x = self.convert_to_normal_function_interval(self.get_seconds(self.astronomical_twilight_begin),
                self.get_seconds(self.astronomical_twilight_end), 0, 6, now)
        #FIXME control variables existence
        return self._normal_function(x, config.min_br, config.max_br)
