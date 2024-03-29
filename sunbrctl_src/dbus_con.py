import pydbus
from gi.repository import GLib
from sys import stderr

BUS_NAME='org.jogme.sunbrctl'

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
            <interface name='org.jogme.sunbrctl'>
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
    try:
        bus.publish(BUS_NAME, BusDriver(hw))
    except:
        print('Could not publish on dbus;'
              'an another instance of this program is already running.', file=stderr)
        exit(-1)
    loop.run()
