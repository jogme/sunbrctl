# Main file of the app 'name_of_the_app'
# The application is for controlling display brightness
# depending on current time
# author: jogme

import subprocess

class HwBrightnessControl:
    #get current brightness
    def _get_br():
        return float(subprocess.run(["xbacklight", "-get"], capture_output=True, text=True).stdout[:-1])

    #set new brightness
    def _set_br(new_br):
        subprocess.run(["xbacklight", "-set", str(new_br)])

    #add or subtract from current brightness
    def _change_br(add):
        current = _get_br()
        _set_br(current+add)

    #_change_br(10)
    #_change_br(-10)

t = TimeManager
