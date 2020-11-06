import os
import struct
import array
import threading
import time
import sys
from fcntl import ioctl


"""
Class to read an xbox controller, works best with the xbox one controller.

Create the object with the path to the device in "/dev/input/", and start
the read loop on another thread. After which you can request the states of the controller via
request_button and request_axis. Finally, stop the read loop with the 
terminate method.

Example provided below.
"""


class Xbone():

    def __init__(self, path_to_device):
        self.device = path_to_device
        self.running = True

        self.axis_states = dict()
        self.button_states = dict()

        # These constants were borrowed from linux/input.h
        axis_names = {
            0x00: 'x',
            0x01: 'y',
            0x02: 'z',
            0x03: 'rx',
            0x04: 'ry',
            0x05: 'rz',
            0x06: 'trottle',
            0x07: 'rudder',
            0x08: 'wheel',
            0x09: 'gas',
            0x0a: 'brake',
            0x10: 'hat0x',
            0x11: 'hat0y',
            0x12: 'hat1x',
            0x13: 'hat1y',
            0x14: 'hat2x',
            0x15: 'hat2y',
            0x16: 'hat3x',
            0x17: 'hat3y',
            0x18: 'pressure',
            0x19: 'distance',
            0x1a: 'tilt_x',
            0x1b: 'tilt_y',
            0x1c: 'tool_width',
            0x20: 'volume',
            0x28: 'misc',
        }

        button_names = {
            0x120: 'trigger',
            0x121: 'thumb',
            0x122: 'thumb2',
            0x123: 'top',
            0x124: 'top2',
            0x125: 'pinkie',
            0x126: 'base',
            0x127: 'base2',
            0x128: 'base3',
            0x129: 'base4',
            0x12a: 'base5',
            0x12b: 'base6',
            0x12f: 'dead',
            0x130: 'a',
            0x131: 'b',
            0x132: 'c',
            0x133: 'x',
            0x134: 'y',
            0x135: 'z',
            0x136: 'tl',
            0x137: 'tr',
            0x138: 'tl2',
            0x139: 'tr2',
            0x13a: 'select',
            0x13b: 'start',
            0x13c: 'mode',
            0x13d: 'thumbl',
            0x13e: 'thumbr',

            0x220: 'dpad_up',
            0x221: 'dpad_down',
            0x222: 'dpad_left',
            0x223: 'dpad_right',

            # XBox 360 controller uses these codes.
            0x2c0: 'dpad_left',
            0x2c1: 'dpad_right',
            0x2c2: 'dpad_up',
            0x2c3: 'dpad_down',
        }

        self.axis_map = []
        self.button_map = []

        with open(self.device, 'rb') as jsdev:
            ""
            buf = array.array('B', [0])
            ioctl(jsdev, 0x80016a11, buf)
            num_axes = buf[0]

            buf = array.array('B', [0])
            ioctl(jsdev, 0x80016a12, buf)
            num_buttons = buf[0]

            buf = array.array('B', [0] * 0x40)
            ioctl(jsdev, 0x80406a32, buf)

            for axis in buf[:num_axes]:
                axis_name = axis_names.get(axis, 'unknown(0x%02x)' % axis)
                self.axis_map.append(axis_name)
                self.axis_states[axis_name] = 0.0

            buf = array.array('H', [0] * 200)
            ioctl(jsdev, 0x80406a34, buf)

            for btn in buf[:num_buttons]:
                btn_name = button_names.get(btn, 'unknown(0x%03x)' % btn)
                self.button_map.append(btn_name)
                self.button_states[btn_name] = 0

    def terminate(self):
        self.running = False

    def read(self):
        """
        Main loop. Records all the controller states in a dictionary. 
        """
        with open(self.device, 'rb') as jsdev:
            while self.running:
                evbuf = jsdev.read(8)

                if evbuf:
                    _, value, type, number = struct.unpack('IhBB', evbuf)

                    if type & 0x01:
                        button = self.button_map[number]
                        if button:
                            self.button_states[button] = value

                    if type & 0x02:
                        axis = self.axis_map[number]
                        if axis:
                            self.axis_states[axis] = round(value / 32767.0, 1)

                time.sleep(0.001)

    def request_axis(self, axis):
        """
        Given the name of an axis as a string, return its value in the axis_states
        """
        return self.axis_states[axis]

    def request_button(self, button):
        """
        Given the name of abutton as a string, return its value in the button_states
        """
        return self.button_states[button]


if __name__ == "__main__":

    js = Xbone('/dev/input/js1')

    x = threading.Thread(target=js.read)
    x.daemon = True
    x.start()

    print(js.button_map)
    print(js.axis_map)

    # prints the x and y axis of the right stick, press select to terminate the loop
    while js.running:
        print(js.request_axis('rx'), js.request_axis('ry'))
        if js.request_button('select'):
            js.terminate()

