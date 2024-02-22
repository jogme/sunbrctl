from os import path
from subprocess import run
from .config import config
from time import sleep

class Hooker:
    morning_time = None
    evening_time = None

    def __init__(self):
        if 'hooks' in config:
            if 'morning_time' in config['hooks']:
                self.morning_time = config['hooks']['morning_time']
            if 'evening_time' in config['hooks']:
                self.evening_time = config['hooks']['evening_time']

    def do_routine(self, which, wait=0, dynamic=True):
        if wait:
            sleep(wait)
        r = config['hooks'][which+'_scripts_static']
        for s in r:
            run(s, shell=True)
