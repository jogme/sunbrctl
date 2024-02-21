# Main file of the app 'sunrise-brightness-control'
# The application is for controlling display brightness
# depending on current time
# author: jogme

import argparse
from time import sleep
from multiprocessing import Process
from sys import stderr

import config
import dbus_con
from hw_brightness_control import HwBrightnessControl

def updater(hw):
    while True:
        sleep(config.sleep_time_s)
        hw.set_br()

def parse_arguments():
    parser = argparse.ArgumentParser(
                        prog='BrightnessControl',
                        description='automatic monitor brightness control')
    parser.add_argument('-v', action='store_true', help='Enable debug logs')
    parser.add_argument('-e', '--external', action='store_true', default=False, help='Enable external monitor')
    parser.add_argument('-c', '--change', type=int, help='Change brightness. If used with external option, \
                        changes the external monitors brightness. The value should be given as a percentage \
                        (-100 - 100). Either decreases or increases depending in the value.')
    args = parser.parse_args()

    if args.v:
        config.v = True
    config.external = args.external

    if args.change:
        if args.change < -100 or args.change > 100:
            print('The change value is out of bound.', file=stderr)
            exit(-1)
        dbus_con.send_change(args.change, args.external)
        return 0

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

    # publish server and run the main loop
    dbus_con.publish_dbus(hw)
