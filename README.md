# sunrise-brightness-control
Brightness control based on the position of the sun

Setting the monitor's brightness level through the day and sleeps at night.
In addition, it is able to run a bash script specified in the config file at
sunrise and sunset. This enables f.e. to define two different rices for day
and night.

To config the brightnessControl check `config.py.def` file.

To use the control hook `python main.py` to your startup.

The main.py can be run with options:
- '-v' for debug messages
- '-e' for supporting one external monitor

#TODO
what to do to make ddcutil work:
- add sudo permission without pswd to run ddcutil
  in sudoers file add the line: ```USER_NAME HOST_NAME= NOPASSWD /path/to/ddcutil```
- load kernel module `i2c_dev`
