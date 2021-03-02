from os import path
from subprocess import run
import config

class Hooker:
    routine_paths = ['./', '~/Projects/brightnessControl/']
    morning_time = None
    evening_time = None
    morning_r = None
    evening_r = None

    def __init__(self):
        for r in self.routine_paths:
            if r[0] == '~':
                r = path.expanduser(r)
            if not self.morning_r and path.exists(r+'morning_routine'):
                self.morning_r = r+'morning_routine'
            if not self.evening_r and path.exists(r+'evening_routine'):
                self.evening_r = r+'evening_routine'

        try:
            self.morning_time = config.morning
        except NameError:
            self.morning_r = None
        try:
            self.evening_time = config.evening
        except NameError:
            self.evening_r = None

    def get_hooks(self):
        return [self.morning_time if self.morning_r is not None else False, \
                self.evening_time if self.evening_r is not None else False]
    def _do_routine(self, r_type):
        if r_type == 0:
            r = self.morning_r
        else:
            r = self.evening_r
        with open(r, 'r') as f:
            scripts = f.read().split('\n')
        scripts = scripts[:-1] if not len(scripts[-1]) else scripts
        for s in scripts:
            run(s + " disown", shell=True)
    def do_morning(self):
        self._do_routine(0)
    def do_evening(self):
        self._do_routine(1)
