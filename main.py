# Main file of the app 'name_of_the_app'
# The application is for controlling display brightness
# depending on current time
# author: jogme

import subprocess

import hw_brightness_control as hw_control
import timeManager

t = TimeManager()

def set_br():
    hw_control.set_br(t.get_current_br)

if __name__ == "__main__":
    set_br()
