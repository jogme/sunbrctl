from os import path
from subprocess import run
from config import config

class Hooker:
    morning_time = None
    evening_time = None

    def __init__(self):
        if 'hooks' in config:
            if 'morning_time' in config['hooks']:
                self.morning_time = config['hooks']['morning_time']
            if 'evening_time' in config['hooks']:
                self.evening_time = config['hooks']['evening_time']

    def _do_routine(self, r_type):
        if r_type == 0:
            r = config['hooks']['morning_scripts_static']
        else:
            r = config['hooks']['evening_scripts_static']
        for s in r:
            run(s, shell=True)
    def do_morning(self):
        self._do_routine(0)
    def do_evening(self):
        self._do_routine(1)
