# sunbrctl
### Brightness control using the sun position.
Automatic brightness controller on notebook screen or an additional
external monitor. Running hook scripts on sunrise and sunset.
Supports linux only.

For further info, run `sunbrctl -h`.

## Install
- From the dir setup:
    - Copy the config file to `~/.config/sunbrctl`
    - Set up your own config
    - For systemd use the `sunbrctl.service` file

what to do to make ddcutil work:

- add sudo permission without pswd to run ddcutil
  in sudoers file add the line: ```USER_NAME HOST_NAME= NOPASSWD /path/to/ddcutil```
- load kernel module `i2c_dev`

## TODO
- Automatic install with python
