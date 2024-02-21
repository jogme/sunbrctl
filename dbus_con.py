import pydbus
from gi.repository import GLib

BUS_NAME='org.jogme.sunrise_brightness_control'

# client
def dbus_connect():
    return pydbus.SessionBus().get(BUS_NAME)

def send_change(value, external=False):
    dbus_connect().Change(value, external)
def send_set(value, external=False):
    dbus_connect().Set(value, external)

class BusDriver(object):
    """
        <node>
            <interface name='org.jogme.sunrise_brightness_control'>
                <method name='Change'>
                    <arg type='i' name='val' direction='in'/>
                    <arg type='b' name='ext' direction='in'/>
                </method>
                <method name='Set'>
                    <arg type='i' name='val' direction='in'/>
                    <arg type='b' name='ext' direction='in'/>
                </method>
            </interface>
        </node>
    """
    def __init__(self, hw):
        self.hw = hw
    def Change(self, val, ext):
        self.hw.change_br(val, ext)
    def Set(self, val, ext):
        self.hw.set_br_manual(val, ext)

def publish_dbus(hw):
    bus = pydbus.SessionBus()
    loop = GLib.MainLoop()
    bus.publish(BUS_NAME, BusDriver(hw))
    loop.run()
