import subprocess

from .config import config
from .timeManager import TimeManager
from .debug import debug

MANUAL_NONE = 0
MANUAL_UP = 1
MANUAL_DOWN = 2

class HwBrightnessControl:
    time_manager = None
    was_manual = MANUAL_NONE

    def __init__(self):
        self.time_manager = TimeManager()
        self.set_first_br()

    #get current brightness
    def get_br(self, external=False):
        if external:
            return int(subprocess.run(['sudo', 'ddcutil', 'getvcp', '-d', '1', '10'], \
                       capture_output=True, text=True).stdout.split('current value =    ')[1].split(',')[0])
        else:
            return int(float(subprocess.run(["xbacklight", "-get"], capture_output=True, text=True).stdout[:-1]))

    def set_br_manual(self, val, ext):
        if val < 2:
            debug('set_br_manual: val would be smaller than 2, setting 2')
            new_br = 2
        if val > 100:
            debug('set_br_manual: val would be greater than 100, setting 100')
            new_br = 100
        if ext:
            debug('set_br_manual: setting ddcutil')
            #for now if the monitor is not connected, the call will fail and nothing happens
            subprocess.run(['sudo', 'ddcutil', 'setvcp', '-d', '1', '10', str(val)])
        else:
            debug('set_br_manual: setting xbacklight')
            subprocess.run(["xbacklight", "-set", str(val)])
    #set new brightness
    def set_br(self):
        if self.was_manual != MANUAL_NONE:
            return
        current = self.get_br()
        new_br = self.time_manager.get_current_br(config['internal_monitor']['min_br'], \
                                                  config['internal_monitor']['max_br'])
        debug('set_br: current: {}, new: {}'.format(current, new_br))

        if current != new_br and abs(current-new_br) > config['internal_monitor']['update_threshold']:
            self.set_br_manual(new_br, False)

        #set the external too
        if 'external_monitor' in config:
            current_external = self.get_br(external=True)
            new_br = self.time_manager.get_current_br(config['external_monitor']['min_br'], \
                                                      config['external_monitor']['max_br'])
            if self.current_external != new_br and \
               abs(self.current_external-new_br) < config['external_monitor']['update_threshold']:
                   self.set_br_manual(new_br, True)

    #set new brightness for the first time
    def set_first_br(self):
        new_br = self.time_manager.get_current_br(config['internal_monitor']['min_br'], \
                                    config['internal_monitor']['max_br'], first=True)
        debug('set_first_br: setting internal to: {}'.format(new_br))
        subprocess.run(["xbacklight", "-set", str(new_br)])
        if 'external_monitor' in config:
            new_br = self.time_manager.get_current_br(config['external_monitor']['min_br'], \
                                    config['external_monitor']['max_br'], first=True)
            debug('set_first_br: setting external to: {}'.format(new_br))
            subprocess.run(['ddcutil', 'setvcp', '-d', '1', '10', str(new_br)])

    #add or subtract from current brightness
    def change_br(self, add, external):
        current = self.get_br(external=external)
        debug('change_br: current brightness: {}'.format(current))
        new_br = current+add
        if new_br < 2:
            debug('change_br: new_br would be smaller than 2, setting 2')
            new_br = 2
        if new_br > 100:
            debug('change_br: new_br would be greater than 100, setting 100')
            new_br = 100
        debug('change_br: new brightness: {}'.format(new_br))
        if external:
            debug('change_br: setting: {} on external'.format(new_br))
            subprocess.run(['ddcutil', 'setvcp', '-d', '1', '10', str(new_br)])
        else:
            debug('change_br: setting: {} on internal'.format(new_br))
            subprocess.run(["xbacklight", "-set", str(new_br)])
        if add < 0:
            if self.was_manual == MANUAL_DOWN:
                self.was_manual = MANUAL_NONE
                self.set_br()
            else:
                self.was_manual = MANUAL_UP
        else:
            if self.was_manual == MANUAL_UP:
                self.was_manual = MANUAL_NONE
                self.set_br()
            else:
                self.was_manual = MANUAL_DOWN
