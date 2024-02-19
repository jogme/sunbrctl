# Main file of the app 'name_of_the_app'
# The application is for controlling display brightness
# depending on current time
# author: jogme

from timeManager import TimeManager
from hw_brightness_control import HwBrightnessControl
from hooker import Hooker
from updater import Updater

class Mediator:
    time_manager = None
    updater = None
    pimp = None
    hw = None
    v = False
    external = False

    def __init__(self, v, e):
        self.v = v
        self.external = e
        self.pimp = Hooker()
        self.time_manager = TimeManager(self, enable_hooks=self.pimp.get_hooks())
        self.updater = Updater(self)
        self.hw = HwBrightnessControl(self)
        self.hw.set_first_br(self.time_manager.get_current_br(order='first'))
    def notify(self, sender, event=None):
        self.debug('notify: message from: {}'.format(sender))
        if type(sender) is Updater:
            self.hw.set_br(self.time_manager.get_current_br())
        elif type(sender) is TimeManager:
            if event == 'h_m':
                self.debug('doing morning routine')
                self.pimp.do_morning()
            elif event == 'h_e':
                self.debug('doing evening routine')
                self.pimp.do_evening()
    def debug(self, message):
        if self.v:
            print('debug: ' + message)
            with open('/home/mountain/brightnessControl.log', 'a') as f:
                # write a logfile when run as a daemon
                f.write(message + '\n')
