# Main file of the app 'name_of_the_app'
# The application is for controlling display brightness
# depending on current time
# author: jogme

from timeManager import TimeManager
from hw_brightness_control import HwBrightnessControl
from updater import Updater

import config

class Mediator:
    time_manager = None
    updater = None
    hw = None
    v = False
    external = False
    min_br = 5
    max_br = 95

    def __init__(self, v, e):
        self.v = v
        self.external = e
        self.time_manager = TimeManager(self)
        self.updater = Updater(self)
        self.hw = HwBrightnessControl(self)
        self.hw.set_first_br(self.time_manager.get_current_br(order='first'))
        try:
            self.min_br = config.min_br
        except:
            # keep default
            pass
        try:
            self.max_br = config.max_br
        except:
            # keep default
            pass
    def notify(self, sender, event=None):
        self.debug('notify: message from: {}'.format(sender))
        if type(sender) is Updater:
            self.hw.set_br(self.time_manager.get_current_br())
    def debug(self, message):
        if self.v:
            print('debug: ' + message)
            with open('/home/mountain/brightnessControl.log', 'a') as f:
                # write a logfile when run as a daemon
                f.write(message + '\n')
