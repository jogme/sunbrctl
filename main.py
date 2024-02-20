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
    parser.add_argument('-v', action='store_true', help='Enable debug logs')
    parser.add_argument('-e', '--external', action='store_true', help='Enable external monitor')
    parser.add_argument('-s', '--set', type=int, help='Set brightness. If used with external option, \
                        sets the external monitors brightness. The value should be given as a percentage \
                        (0-100).')
    args = parser.parse_args()

    if args.set:
        if args.set < 0 or args.set > 100:
            print('The set value is out of bound.', file=stderr)
            exit(-1)
        # FIXME send the set signal for the main prog if running
    else:
        mediator = Mediator(args.v, args.external)

        while True:
            mediator.updater.update()
            sleep(config.sleep_time_s)
