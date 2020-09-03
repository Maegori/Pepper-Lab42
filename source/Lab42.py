
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

MID_FRONT = 8
DETECTION_RANGE = 1.5
TARGET_DISTANCE = 0.42


class Lab42(object):

    def __init__(self, app):
        super(Lab42, self).__init__()
        app.start()
        session = app.session

        # Get services
        self.memoryService = session.service("ALMemory")
        self.motionService = session.service("ALMotion")
        self.laserService = session.service("ALLaser")
        self.postureService = session.service("ALRobotPosture")
        self.awarenessService = session.service("ALBasicAwareness")
        self.tts = session.service("ALTextToSpeech")

        # Set subscriptions
        self.touch = self.memoryService.subscriber("TouchChanged")
        self.block = self.memoryService.subscriber(
            "ALMotion/MoveFailed"
        )

        # Connect callbacks
        self.id = self.touch.signal.connect(
            functools.partial(self.onTouched, "TouchChanged")
        )
        self.block.signal.connect(
            functools.partial(self.onBlocked, "ALMotion/MoveFailed")
        )

        # TTS settings
        self.tts.setLanguage("Dutch")
        self.tts.setParameter("pitchShift", 1.1)
        self.tts.setParameter("speed", 90)

        # Input handling
        self.running = True
        self.controller = Xbone('/dev/input/js1')

        # Run behaviour
        print("Start Demo")
        self.demo()

    def demo(self):
        """Main control loop."""

        self.motionService.wakeUp()
        self.motionService.setOrthogonalSecurityDistance(0.1)
        self.motionService.setCollisionProtectionEnabled("Arms", False)
        self.motionService.setExternalCollisionProtectionEnabled("All", False)
        self.awarenessService.setTrackingMode("Head")
        self.motionService.moveInit()

        t = threading.Thread(target=self.controller.read)
        t.deamon = True
        t.start()

        while self.running:
            time.sleep(0.001)
            self.handleEvents()

        self.motionService.setOrthogonalSecurityDistance(0.4)
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.motionService.setExternalCollisionProtectionEnabled(
            "All", True)
        self.awarenessService.setTrackingMode("MoveContextually")
        self.motionService.rest()

    def handleEvents(self):
        self.motionService.moveToward(-self.controller.request_axis(
            'ry'), 0, -self.controller.request_axis('rx'))
        if self.controller.request_button('a'):
            self.motionService.stopMove()
            self.running = False
        elif self.controller.request_button('b'):
            self.motionService.stopMove()
            self.running = False

    def onBlocked(self, strVarName, value):
        """Print information when movement is blocked."""

        print(
            "[FAIL] -- CAUSE={}, STATUS={}, LOCATION={}"
            .format(value[0], value[1], value[2])
        )

    def onTouched(self, strVarName, value):
        self.touch.signal.disconnect(self.id)

        arms = set(["LArm", "RArm"])
        parts = set()

        for p in value:
            if p[1]:
                parts.add(p[0])

        if arms.intersection(parts):
            # self.tts.say("Gaan we op een wandeling?")
            self.motionService.setStiffnesses(arms, 0.1)
        else:
            self.motionService.setStiffnesses(arms, 1)

        self.id = self.touch.signal.connect(
            functools.partial(self.onTouched, "TouchChanged"))

    def alignHit(self):
        """Align with the object and play the hit animation after a cue."""
        self.awarenessService.setTrackingMode("WholeBody")
        self.align()
        self.animate()
        self.awarenessService.setTrackingMode("MoveContextually")
        # self.motionService.rest()

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

    def animate(self):
        self.motionService.setExternalCollisionProtectionEnabled("Arms", False)
        self.motionService.moveToward(0, 0, 0.69)
        time.sleep(1.1)
        self.motionService.stopMove()

        animation = dict()
        names = []
        times = []
        keys = []
        isAbsolute = True

        with open("animations/"+sys.argv[2]+".pickle", "rb") as f:
            animation = pickle.load(f)

        for key in animation.keys():
            names.append(key)
            times.append(animation[key][0])
            keys.append(animation[key][1])

        self.postureService.goToPosture("StandInit", 1)
        self.motionService.angleInterpolation(names, keys, times, isAbsolute)
        time.sleep(1.0)
        self.motionService.setExternalCollisionProtectionEnabled("Arms", True)

    def approach(self, keys):
        """Move closer until the object is in the target range."""

        print("Approaching target")
        scan = self.memoryService.getListData(keys)

        while min(scan) > TARGET_DISTANCE:
            self.motionService.moveToward(0.3, 0, 0)
            scan = self.memoryService.getListData(keys)

        self.motionService.stopMove()
        print("In range of target")
        return np.argmin(scan)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="146.50.60.38",
                        help="Robot IP address. On robot or Local Naoqi: use '146.50.60.38'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--animation", type=str,
                        help="Name of the animation to play")
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
    nav = Lab42(app)
    app.run()


# Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value
# Device/SubDeviceList/Pla`tform/Back/Sonar/Sensor/Value
