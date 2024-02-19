# Main file of the app 'sunrise-brightness-control'
# The application is for controlling display brightness
# depending on current time
# author: jogme

import argparse
from time import sleep

import config
from mediator import Mediator

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog='BrightnessControl',
                        description='automatic monitor brightness control')
    parser.add_argument('-v', action='store_true')
    parser.add_argument('-e', '--external', action='store_true')
    args = parser.parse_args()

    mediator = Mediator(args.v, args.external)

    while True:
        mediator.updater.update()
        sleep(config.sleep_time_s)
