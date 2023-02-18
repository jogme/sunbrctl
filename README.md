# sunrise-brightness-control
Brightness control according the sun position

#TODO
what to do to make ddcutil work:
- add sudo permission without pswd to run ddcutil
  in sudoers file add the line: ```USER_NAME HOST_NAME= NOPASSWD /path/to/ddcutil```
- load kernel module `i2c_dev`
