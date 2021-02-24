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
        if abs(int(HwBrightnessControl.get_br())-new_br) < new_br / 3:
            subprocess.run(["xbacklight", "-set", str(new_br)])

    #set new brightness for the first time
    def set_first_br(new_br):
        if new_br < config.min_br:
            new_br = config.min_br
        if new_br > config.max_br:
            new_br = config.max_br
        subprocess.run(["xbacklight", "-set", str(new_br)])

    #add or subtract from current brightness
    def change_br(add):
        current = get_br()
        set_br(current+add)

    #change_br(10)
    #change_br(-10)
