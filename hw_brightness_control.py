import subprocess

import config

class HwBrightnessControl:
    #get current brightness
    def get_br():
        return float(subprocess.run(["xbacklight", "-get"], capture_output=True, text=True).stdout[:-1])

    #set new brightness
    def set_br(new_br):
        if new_br < config.min_br:
            new_br = config.min_br
        if new_br > config.max_br:
            new_br = config.max_br
        subprocess.run(["xbacklight", "-set", str(new_br)])

    #add or subtract from current brightness
    def change_br(add):
        current = _get_br()
        _set_br(current+add)

    #_change_br(10)
    #_change_br(-10)
