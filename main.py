# Main file of the app 'name_of_the_app'
# The application is for controlling display brightness
# depending on current time
# author: jogme

from time import sleep

import config
from mediator import Mediator

mediator = Mediator()

if __name__ == "__main__":
    while True:
        mediator.updater.update()
        sleep(config.sleep_time_s)
