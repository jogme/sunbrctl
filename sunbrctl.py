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

from sunbrctl_src.config import config, processes
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
    parser.add_argument('--config', type=str, default=None, help='Path to config file to be used. \
                        Load only this config.')
    args = parser.parse_args()

    if args.change:
        if args.change < -100 or args.change > 100:
            print('The change value is out of bound.', file=stderr)
            exit(-1)
        try:
            dbus_con.send_change(args.change, args.external)
        except:
            exit(-1)
        return 0
    elif args.set:
        if args.set < 0 or args.set > 100:
            print('The set value is out of bound.', file=stderr)
            exit(-1)
        try:
            dbus_con.send_set(args.set, args.external)
        except:
            exit(-1)
        return 0

    config['v'] = args.v
    config['external'] = args.external

    return args

def _check_config():
    c = config
    #mandatory
    if not 'position' in c:
        debug('check_config: no \'position\' parameter given')
        return -1
    if not 'lat' in c['position'] or \
       not 'lng' in c['position']:
        debug('check_config: no \'lat\' or \'lng\' parameter given in \'position\'')
        return -1
    if not 'internal_monitor' in c and \
       not 'external_monitor' in c and \
       not 'hooks' in c:
        debug('check_config: no internal or external monitor given or hooks.')
        return -2

    #optional
    if not 'utc' in c['position']:
        config['position']['utc'] = 0
        debug('check_config: no \'utc\' parameter given, setting default to 0')
    if not 'updater' in c or \
       not 'sleep_time_s' in c['updater']:
        # default to 5mins
        debug('check_config: no \'sleep_time_s\' parameter given, setting default to 300s')
        config['updater'] = {'sleep_time_s':300}

    if 'hooks' in c:
        h = c['hooks']
        if not 'morning_on_startup' in h:
            debug('check_config: no \'morning_on_startup\' parameter given in hooks, '
                  'setting default to false')
            h['morning_on_startup'] = False
        if not 'evening_time' in h:
            if 'evening_scripts_static' in h or \
               'evening_scripts_dynamic' in h:
                debug('check_config: no \'evening_time\' parameter given in hooks, '
                      'setting default to astronomical')
                h['evening_time'] = 'astronomical'
            else:
                h['evening_time'] = None
        if not 'morning_time' in h:
            if 'morning_scripts_static' in h or \
               'morning_scripts_dynamic' in h:
                debug('check_config: no \'morning_time\' parameter given in hooks, '
                      'setting default to astronomical')
                h['morning_time'] = 'astronomical'
            else:
                h['morning_time'] = None
        if not 'evening_scripts_static' in h and \
           not 'evening_scripts_dynamic' in h and \
           not 'morning_scripts_static' in h and \
           not 'morning_scripts_dynamic' in h:
            debug('check_config: no scripts given in hooks, turning hooks off.')
            del c['hooks']

    if 'internal_monitor' in c:
        i = c['internal_monitor']
        if not 'update_threshold' in i:
            debug('check_config: no \'update_threshold\' parameter given in internal monitor, '
                  'setting default to 5')
            i['update_threshold'] = 5
        if not 'min_br' in i:
            debug('check_config: no \'min_br\' parameter given in internal monitor, '
                  'setting default to 2')
            i['min_br'] = 2
        if not 'max_br' in i:
            debug('check_config: no \'max_br\' parameter given in internal monitor, '
                  'setting default to 100')
            i['max_br'] = 100

    if 'external_monitor' in c:
        e = c['external_monitor']
        if not 'update_threshold' in e:
            debug('check_config: no \'update_threshold\' parameter given in external monitor, '
                  'setting default to 5')
            e['update_threshold'] = 5
        if not 'min_br' in e:
            debug('check_config: no \'min_br\' parameter given in external monitor, '
                  'setting default to 2')
            e['min_br'] = 2
        if not 'max_br' in e:
            debug('check_config: no \'max_br\' parameter given in external monitor, '
                  'setting default to 100')
            e['max_br'] = 100

    return 0

def load_config(c_file=None):
    if c_file:
        config_files = [c_file]
    else:
        # last the most important
        config_files = ['/etc/sunbrctl/config',
                        '~/.config/sunbrctl/config']

    for x in config_files:
        x = path.expanduser(x)
        try:
            with open(x, 'r') as f:
                config.update(load(f, Loader))
        except FileNotFoundError:
            debug("Could not find config file at '{}'".format(x))
            continue
    return _check_config()

if __name__ == "__main__":
    args = parse_arguments()
    if args == 0:
        exit(0)
    r = load_config(args.config)
    if r == -1:
        print('The config is wrong. Check debug messages', file=stderr)
        exit(-1)
    elif r == -2:
        print('Nothing to do. Exiting.')
        exit(0)

    BaseManager.register('HwBrightnessControl', HwBrightnessControl)
    manager = BaseManager()
    manager.start()
    hw = manager.HwBrightnessControl()

    # give time to boot
    sleep(30)
    p = Process(target=updater, args=[hw])
    p.start()
    processes.append(p)
    
    # at app exit terminate the child processes
    try:
        # publish server and run the main loop
        dbus_con.publish_dbus(hw)
    finally:
        for x in processes:
            x.terminate()
