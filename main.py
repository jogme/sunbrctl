# Main file of the app 'name_of_the_app'
# The application is for controlling display brightness
# depending on current time
# author: jogme

from time import sleep

from hw_brightness_control import HwBrightnessControl
from timeManager import TimeManager
import config

t = TimeManager()

def set_br():
    while True:
        HwBrightnessControl.set_br(t.get_current_br())
        sleep(config.sleep_time_s)

if __name__ == "__main__":
    set_br()
