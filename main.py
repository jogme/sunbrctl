# Main file of the app 'name_of_the_app'
# The application is for controlling display brightness
# depending on current time
# author: jogme

from time import sleep

from hw_brightness_control import HwBrightnessControl
from timeManager import TimeManager
from os import path
import config

routine_paths = {}
t = None

if path.exists('morning_routine'):
    routine_paths['morning'] = 'morning_routine'
if path.exists('evening_routine'):
    routine_paths['evening'] = 'evening_routine'

if len(routine_paths):
    t = TimeManager(routine_paths)
else:
    t = TimeManager()
    del routine_paths

def set_br():
    HwBrightnessControl.set_first_br(t.get_current_br())
    while True:
        HwBrightnessControl.set_br(t.get_current_br())
        sleep(config.sleep_time_s)

if __name__ == "__main__":

    set_br()
