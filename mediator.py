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

    def __init__(self):
        self.pimp = Hooker()
        self.time_manager = TimeManager(self, enable_hooks=self.pimp.get_hooks())
        self.updater = Updater(self)
        HwBrightnessControl.set_first_br(self.time_manager.get_current_br())
    def notify(self, sender, event=None):
        if type(sender) is Updater:
            HwBrightnessControl.set_br(self.time_manager.get_current_br())
        elif type(sender) is TimeManager:
            if event == 'h_m':
                self.pimp.do_morning()
            elif event == 'h_e':
                self.pimp.do_evening()
