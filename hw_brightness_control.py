import subprocess
import re

import config
from timeManager import TimeManager
from debug import debug

class HwBrightnessControl:
    external_monitors = dict()
    time_manager = None

    def __init__(self):
        self.time_manager = TimeManager()
        self.set_first_br()

    #get current brightness
    def get_br(self, external=False):
        if external:
            return int(subprocess.run(['sudo', 'ddcutil', 'getvcp', '-d', '1', '10'], capture_output=True, text=True).stdout.split('current value =    ')[1].split(',')[0])
        else:
            return int(float(subprocess.run(["xbacklight", "-get"], capture_output=True, text=True).stdout[:-1]))

    def set_br_manual(self, val, ext):
        if ext:
            debug('set_br_manual: setting ddcutil')
            #for now if the monitor is not connected, the call will fail and nothing happens
            subprocess.run(['sudo', 'ddcutil', 'setvcp', '-d', '1', '10', str(val)])
        else:
            debug('set_br_manual: setting xbacklight')
            subprocess.run(["xbacklight", "-set", str(val)])
    #set new brightness
    def set_br(self):
        current = self.get_br()
        new_br = self.time_manager.get_current_br()
        debug('set_br: current: {}, new: {}'.format(current, new_br))

        if current != new_br and abs(current-new_br) > config.user_threshold:
            self.set_br_manual(new_br, False)

        #set the external too
        if config.external:
            current_external = self.get_br(external=True)
            if self.current_external != new_br and \
               abs(self.current_external-new_br) < config.user_threshold:
                   self.set_br_manual(new_br, True)

    #set new brightness for the first time
    def set_first_br(self):
        new_br = self.time_manager.get_current_br(order='first')
        debug('set_first_br: setting: {}'.format(new_br))
        subprocess.run(["xbacklight", "-set", str(new_br)])
        if config.external:
            subprocess.run(['ddcutil', 'setvcp', '-d', '1', '10', str(new_br)])

    #add or subtract from current brightness
    def change_br(self, add, external):
        current = self.get_br(external=external)
        debug('change_br: current brightness: {}'.format(current))
        new_br = current+add
        debug('change_br: new brightness: {}'.format(new_br))
        if external:
            debug('change_br: setting: {} on external'.format(new_br))
            subprocess.run(['ddcutil', 'setvcp', '-d', '1', '10', str(new_br)])
        else:
            debug('change_br: setting: {} on internal'.format(new_br))
            subprocess.run(["xbacklight", "-set", str(new_br)])
