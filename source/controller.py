"""
FILE: controller.py
AUTHORS: Lex Johan, Niels Rouws
EMAIL: lex.johan@student.uva.nl, niels.rouws@student.uva.nl
DATE: 06/11/2020

DESCRIPTION:
Script to let Pepper walk with an xbox controller. See xbone.py
for more information. Works
"""

import qi
import argparse
import functools
import sys
import time
import io
import struct
import math
import threading

from xbone import Xbone

class Controller(object):

    def __init__(self, app, path_to_js):
        super(Controller, self).__init__()
        app.start()
        session = app.session

        # Get services
        self.memoryService = session.service("ALMemory")
        self.motionService = session.service("ALMotion")

        # create the controller object
        self.js = Xbone(path_to_js)

        # start the reading on a seperate thread
        x = threading.Thread(target=self.js.read)
        x.daemon = True
        x.start()

        # prints the available buttons and axes of the current controller
        print(self.js.button_map)
        print(self.js.axis_map)

        self.control()

    def control(self):

        while self.js.running:
            if self.js.request_button('select'):
                self.js.terminate()

            # get axes of right stick
            x = -self.js.request_axis('ry')
            theta = -self.js.request_axis('rx')

            # if the turning speed is too high, set the forward movement to 0 for smoother turns
            if not -0.45 < theta < 0.45:
                x = 0

            self.motionService.moveToward(x, 0, theta)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="146.50.60.38",
                        help="Robot IP address. On robot or Local Naoqi: use '146.50.60.38'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--path", type=str, default="/dev/input/js0", 
                        help="Path to joystick, default=/dev/input/js0")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["Swing", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
              "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    print("Succesfully connected to Pepper @ tcp://" +
          args.ip + ":" + str(args.port))
    nav = Controller(app, args.path)
    app.run()
