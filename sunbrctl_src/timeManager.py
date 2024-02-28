from datetime import datetime, time
import json
import requests
import math
from time import sleep

from .config import config
from .hooker import Hooker
from .debug import debug

class TimeManager:
    pimp = None
    current_time = time(0,0,0)
    current_day = datetime.now().day

    astronomical_twilight_begin = None
    astronomical_twilight_end = None

    hook_morning_do = True
    hook_evening_do = True

    no_internet = False
    
    def __init__(self):
        self.pimp = Hooker()
        self.get_todays_sunrise()
        if not config['hooks']['morning_on_startup']:
            self.hook_morning_do = False
        self.update_time(True)
    def update_time(self, first=False):
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
        debug("update_time: new_time: " + new_time.strftime("%H:%M:%S"))
        debug("update_time: evening hook time: " + self.pimp.evening_time.strftime("%H:%M:%S"))
        debug("update_time: morning hook time: " + self.pimp.morning_time.strftime("%H:%M:%S"))
        if self.pimp.morning_time and self.hook_morning_do and new_time > self.pimp.morning_time and new_time < self.pimp.evening_time:
            # do not run dynamic scripts when it's the first time
            self.pimp.do_routine('morning', dynamic=(not first))
            self.hook_morning_do = False
        elif self.pimp.evening_time and self.hook_evening_do and (new_time > self.pimp.evening_time or new_time < self.pimp.morning_time):
            self.pimp.do_routine('evening', dynamic=(not first))
            self.hook_evening_do = False
        if not first and new_time > self.astronomical_twilight_end:
            #86400s is a day + 60s to go past midnight
            debug('update_time: going to sleep. Good night!')
            sleep((self.get_seconds(self.astronomical_twilight_end)-86460)*-1)

        self.current_time = new_time
    def get_todays_sunrise(self):
        #using https://sunrise-sunset.org/api
        api_time_format = "%I:%M:%S %p"
        debug('get_todays_sunrise: getting todays sunrise data')
        url = "https://api.sunrise-sunset.org/json?lat={}&lng={}&date=today".format(config['position']['lat'], config['position']['lng'])

        try:
            debug("get_todays_sunrise: {}".format(url))
            r = requests.get(url)
            if(r.status_code != 200):
                return r.status_code
        except (requests.ConnectionError, requests.Timeout) as exception:
            self.no_internet = True

        if self.no_internet:
            debug('get_todays_sunrise: no internet connection')
            try:
                with open("latest.data", "r") as f:
                    res_j = json.load(f)['results']
                    debug('get_todays_sunrise: opened old sunrise data file')
            except:
                while True:
                    try:
                        r = requests.get(url)
                        if(r.status_code != 200):
                            return r.status_code
                        self.no_internet = False
                        break
                    except (requests.ConnectionError, requests.Timeout) as exception:
                        sleep(10)

        else:
            with open("latest.data", "w") as f:
                json.dump(r.json(), f)
                debug('get_todays_sunrise: written new sunrise data to the file')
            res_j = r.json()['results']

        self.astronomical_twilight_begin = datetime.strptime(res_j['astronomical_twilight_begin'], api_time_format).time()
        self.astronomical_twilight_end = datetime.strptime(res_j['astronomical_twilight_end'], api_time_format).time()

        if self.pimp.morning_time == 'civil':
            self.pimp.morning_time = self.datetime.strptime(res_j['civil_twilight_begin'], api_time_format).time()
        elif self.pimp.morning_time == 'nautical':
            self.pimp.morning_time = self.datetime.strptime(res_j['nautical_twilight_begin'], api_time_format).time()
        elif self.pimp.morning_time == 'astronomical':
            self.pimp.morning_time = self.astronomical_twilight_begin

        if self.pimp.evening_time == 'civil':
            self.pimp.evening_time = self.datetime.strptime(res_j['civil_twilight_end'], api_time_format).time()
        elif self.pimp.evening_time == 'nautical':
            self.pimp.evening_time = self.datetime.strptime(res_j['nautical_twilight_end'], api_time_format).time()
        elif self.pimp.evening_time == 'astronomical':
            self.pimp.evening_time = self.astronomical_twilight_end

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
        return int((base**((-(x-4)**4)/2**3))*100)

    #<a,b> is the input interval
    #<c,d> is the output interval
    #x is the number to be converted
    def convert_to_normal_function_interval(self, a, b, c, d, x):
        if a == b:
            raise
        return c+((d-c)/(b-a))*(x-a)

    def get_current_br(self, min_br, max_br, first=False):
        self.update_time(first)
        now = self.get_seconds(self.current_time)
        x = self.convert_to_normal_function_interval(self.get_seconds(self.astronomical_twilight_begin),
                self.get_seconds(self.astronomical_twilight_end), 0, 6, now)
        return self._normal_function(x, min_br, max_br)
