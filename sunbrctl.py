#! /usr/bin/python

# Main file of the app 'sunbrctl'
# The application is for controlling display brightness
# depending on current time and sunrise/sunset.
# author: jogme

import argparse
from time import sleep
from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from sys import stderr
from os import path

from sunbrctl_src.config import config
from sunbrctl_src import dbus_con
from sunbrctl_src.hw_brightness_control import HwBrightnessControl
from sunbrctl_src.debug import debug

def updater(hw):
    while True:
        sleep(config['updater']['sleep_time_s'])
        hw.set_br()

def parse_arguments():
    parser = argparse.ArgumentParser(
                        prog='BrightnessControl',
                        description='automatic monitor brightness control')
    parser.add_argument('-v', action='store_true', default=False, help='Enable debug logs')
    parser.add_argument('-e', '--external', action='store_true', default=False, help='Enable external monitor')
    parser.add_argument('-c', '--change', type=int, help='Change brightness. If used with external option, \
                        change the external monitors brightness. The value should be given as a percentage \
                        (-100 - 100). Either decreases or increases depending in the value.')
    parser.add_argument('-s', '--set', type=int, help='Set specific brightness. If used with external \
                        option, set the external monitors brightness. The value should be given as a \
                        percentage (0 - 100).')
    parser.add_argument('--config', type=str, default=None, help='Path to config file to be used')
    args = parser.parse_args()

    if args.change:
        if args.change < -100 or args.change > 100:
            print('The change value is out of bound.', file=stderr)
            exit(-1)
        dbus_con.send_change(args.change, args.external)
        return 0
    elif args.set:
        if args.set < 0 or args.set > 100:
            print('The set value is out of bound.', file=stderr)
            exit(-1)
        dbus_con.send_set(args.set, args.external)
        return 0

    config['v'] = args.v
    config['external'] = args.external

    return args

def load_config(c_file=None):
    if c_file:
        config_files = [c_file]
    else:
        # last the most important
        config_files = ['/etc/sunrise-brightness-control/config',
                        '~/.config/sunrise-brightness-control/config']

    for x in config_files:
        x = path.expanduser(x)
        try:
            with open(x, 'r') as f:
                config.update(load(f, Loader))
        except FileNotFoundError:
            debug("Could not find config file at '{}'".format(x))
            continue
    if not 'min_br' in config:
        config['min_br'] = 5
    if not 'max_br' in config:
        config['max_br'] = 95

if __name__ == "__main__":
    args = parse_arguments()
    if args == 0:
        exit(0)
    load_config(args.config)

    BaseManager.register('HwBrightnessControl', HwBrightnessControl)
    manager = BaseManager()
    manager.start()
    hw = manager.HwBrightnessControl()

    p = Process(target=updater, args=[hw])
    p.start()
    config.processes.append(p)
    
    try:
        # publish server and run the main loop
        dbus_con.publish_dbus(hw)
    finally:
        print('this works')
        for x in config.processes:
            x.terminate()
