from os import path, environ
from subprocess import run
from .config import config
from .debug import debug
from time import sleep

class Hooker:
    morning_time = None
    evening_time = None

    def __init__(self):
        if 'hooks' in config:
            self.morning_time = config['hooks']['morning_time']
            self.evening_time = config['hooks']['evening_time']

    def _run_scripts(self, r):
        for s in r:
            run(s, shell=True, env=environ)

    def do_routine(self, which, wait=0, dynamic=True):
        if wait:
            sleep(wait)
        if which+'_scripts_static' in config['hooks']:
            r = config['hooks'][which+'_scripts_static']
            self._run_scripts(r)
        if dynamic and which+'_scripts_dynamic' in config['hooks']:
            debug('do_routine: run dynamic scripts')
            r = config['hooks'][which+'_scripts_dynamic']
            self._run_scripts(r)
