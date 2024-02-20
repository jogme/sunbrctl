# Main file of the app 'sunrise-brightness-control'
# The application is for controlling display brightness
# depending on current time
# author: jogme

import argparse
from time import sleep

import config
from hw_brightness_control import HwBrightnessControl

def updater(hw):
    while True:
        hw.set_br()
        sleep(config.sleep_time_s)

def parse_arguments():
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

    return args

def check_config():
    if not hasattr(config, 'min_br'):
        config.min_br = 5
    if not hasattr(config, 'max_br'):
        config.max_br = 95

if __name__ == "__main__":
    check_config()
    args = parse_arguments()
    if args == 0:
        exit(0)
    hw = HwBrightnessControl()

    p = Process(target=updater, args=(hw,))
    p.start()

