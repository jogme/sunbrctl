import subprocess
import re

import config

class HwBrightnessControl:
    external_monitors = dict()
    current_external = 0

    def __init__(self, mediator):
        self.mediator = mediator
    #get current brightness
    def get_br(self):
        return int(float(subprocess.run(["xbacklight", "-get"], capture_output=True, text=True).stdout[:-1]))

    #set new brightness
    def set_br(self, new_br):
        current = self.get_br()
        self.mediator.debug('set_br: current: {}, new: {}'.format(current, new_br))
        if self.mediator.external:
            current_external = subprocess.run(['sudo', 'ddcutil', 'getvcp', '-d', '1', '10'], capture_output=True, text=True).stdout
        if current != new_br and abs(current-new_br) > config.user_threshold:
            self.mediator.debug('set_br: setting xbacklight')
            subprocess.run(["xbacklight", "-set", str(new_br)])
        #set the external too
        if self.mediator.external:
            if self.current_external != new_br and \
               abs(self.current_external-new_br) < config.user_threshold:
                #for now if the monitor is not connected, the call will fail and nothing happens
                self.current_external = new_br
                subprocess.run(['sudo', 'ddcutil', 'setvcp', '-d', '1', '10', str(new_br)])

    #set new brightness for the first time
    def set_first_br(self, new_br):
        self.mediator.debug('set_first_br: setting: {}'.format(new_br))
        subprocess.run(["xbacklight", "-set", str(new_br)])
        if self.mediator.external:
            subprocess.run(['ddcutil', 'setvcp', '-d', '1', '10', str(new_br)])
            self.current_external = new_br

    #add or subtract from current brightness
    def change_br(self, add):
        current = get_br()
        set_br(current+add)
    
    #detect external monitors
    #def get_ext_monitors():
    #    ms = subprocess.run(["sudo", "ddcutil", "detect"], capture_output=True, text=True).stdout
    #    for block in ms.split('\n\n'):
    #        r = re.match('Display [0-9]+', block.split('\n')[0])
    #        if r:
    #            self.external_monitors[r[0].split()[1]] = ['min', 'max']

    #change_br(10)
    #change_br(-10)
