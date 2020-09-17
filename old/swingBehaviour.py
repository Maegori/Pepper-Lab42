
import qi
import argparse
import functools
import sys
import numpy as np

MID_FRONT = 8
DETECTION_RANGE = 1.5
TARGET_DISTANCE = 0.35


class Swing(object):

    def __init__(self, app):
        super(Swing, self).__init__()
        app.start()
        session = app.session

        # Get services
        self.memoryService = session.service("ALMemory")
        self.motionService = session.service("ALMotion")
        self.laserService = session.service("ALLaser")
        self.awarenessService = session.service("ALBasicAwareness")
        self.tts = session.service("ALTextToSpeech")

        # Set subscriptions
        self.block = self.memoryService.subscriber(
            "ALMotion/MoveFailed"
        )
        # Connect callbacks
        self.block.signal.connect(
            functools.partial(self.onBlocked, "ALMotion/MoveFailed")
        )

        # Scripts
        self.hit()

    def onBlocked(self, strVarName, value):
        print(
            "[FAIL] -- CAUSE={}, STATUS={}, LOCATION={}"
            .format(value[0], value[1], value[2])
        )

    def hit(self):
        self.awarenessService.setTrackingMode("WholeBody")
        self.align()
        self.animate()
        self.awarenessService.setTrackingMode("MoveContextually")

    def align(self):
        self.motionService.moveInit()

        keys = [
            "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg" +
            ("0" if i < 10 else "") + str(i) + "/X/Sensor/Value" for i in range(1, 16)
        ]

        phi = 0.0698  # Radians between two adjacent lasers

        while True:
            scan = self.memoryService.getListData(keys)
            target = np.argmin(scan)

            print(
                "Aligning with: {} {}".format(target, scan[target])
            )

            if scan[target] < DETECTION_RANGE:
                if target == MID_FRONT:
                    self.motionService.stopMove()
                    if self.approach(keys) == MID_FRONT:
                        break

                theta = float((MID_FRONT - target) * phi)
                if theta:
                    self.motionService.moveToward(0, 0, theta)

        self.motionService.stopMove()
        print("Target reached and aligned with")

    def approach(self, keys):
        print("Approaching target")
        scan = self.memoryService.getListData(keys)

        while min(scan) > TARGET_DISTANCE:
            self.motionService.moveToward(0.3, 0, 0)
            scan = self.memoryService.getListData(keys)

            # if d > DETECTION_RANGE:
            #     self.motionService.stopMove()
            #     return searchflag?

        self.motionService.stopMove()
        print("In range of target")
        return np.argmin(scan)

    def animate(self):
        self.motionService.setExternalCollisionProtectionEnabled("Arms", False)
        self.tts.say("Bonk")
        self.motionService.setExternalCollisionProtectionEnabled("Arms", True)


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
    swing_motion = Swing(app)
    app.run()
