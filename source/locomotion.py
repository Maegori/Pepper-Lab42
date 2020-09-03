
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


class Navigator(object):

    def __init__(self, app):
        super(Navigator, self).__init__()
        self.app = app
        self.app.start()
        session = app.session

        # Get services
        self.memoryService = session.service("ALMemory")
        self.motionService = session.service("ALMotion")
        self.postureService = session.service("ALRobotPosture")
        self.laserService = session.service("ALLaser")
        self.awarenessService = session.service("ALBasicAwareness")
        self.controller = Xbone('/dev/input/js0')
        self.move()

    def move(self):
        self.motionService.wakeUp()
        self.motionService.setOrthogonalSecurityDistance(0.1)
        self.motionService.setCollisionProtectionEnabled("Arms", False)
        self.motionService.setExternalCollisionProtectionEnabled("All", False)
        self.awarenessService.setTrackingMode("WholeBody")
        self.motionService.moveInit()

        print("Start")

        t = threading.Thread(target=self.controller.read)
        t.deamon = True
        t.start()

        while True:
            time.sleep(0.01)
            self.motionService.moveToward(-self.controller.request_axis(
                'ry'), 0, -self.controller.request_axis('rx'))
            if self.controller.request_button('a'):
                self.motionService.stopMove()
                self.motionService.rest()
                break
            elif self.controller.request_button('b'):
                self.motionService.stopMove()
                self.motionService.rest()
                break

        self.motionService.setOrthogonalSecurityDistance(0.4)
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.motionService.setExternalCollisionProtectionEnabled("All", True)
        self.awarenessService.setTrackingMode("MovecContextually")
        self.motionService.rest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="146.50.60.38",
                        help="Robot IP address. On robot or Local Naoqi: use '146.50.60.38'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

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
    nav = Navigator(app)
    app.run()


# Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value
# Device/SubDeviceList/Pla`tform/Back/Sonar/Sensor/Value
