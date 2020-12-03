# Main file of the app 'name_of_the_app'
# The application is for controlling display brightness
# depending on current time
# author: jogme

from hw_brightness_control import HwBrightnessControl
from timeManager import TimeManager

t = TimeManager()

def set_br():
    HwBrightnessControl.set_br(t.get_current_br())

if __name__ == "__main__":
    set_br()
