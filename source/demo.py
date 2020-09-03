
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
        # self.controller = Xbone('/dev/input/js1')

        # Run behaviour
        print("Start Demo")
        self.test()

    def test(self):
        print("start")
        self.motionService.rest()
        self.motionService.wakeUp()
        self.postureService.goToPosture("StandZero", 0.5)
        self.motionService.setStiffnesses(
            "RArm", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        # while True:
        #     self.motionService.setStiffnesses("RArm", [0, 0, 0, 0, 0, 0])
        #     print(self.motionService.getAngles("RArm", True))

        # self.motionService.angleInterpolation(
        #     ["RShoulderPitch", "RShoulderRoll", "RElbowYaw",
        #         "RElbowRoll", "RWristYaw", "RHand"],
        #     angles,
        #     [1.0 for _ in range(6)], True)
        speed = 0.2
        goal = [1, -0.5, 1.61, 1.05, 1.55, 0]

        self.motionService.setAngles(
            "RArm", goal, speed)

        while True:
            current = self.motionService.getAngles("RArm", True)
            if sum([(y-x)**2 for x, y in zip(current, goal)]) < 0.2:
                break

        print("Waiting in pose...")
        while not self.isTouched("RArm"):
            continue

        print("end")
        # self.postureService.goToPosture("Stand", 0.5)
        self.motionService.setCollisionProtectionEnabled("Arms", True)

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

    def holdPose(self, poseName, speed, chains):
        """
        Stays in specified pose until one of the sensors in the chains is touched.
        """
        cp = self.motionService.getCollisionProtectionEnabled("Arms")
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.postureService.goToPosture(poseName, speed)

        while not self.postureService._isRobotInPosture(poseName, 26, 2):
            continue

        while not self.isTouched(chains):
            angles = self.motionService.getAngles("Body", True)
            self.motionService.setAngles("Body", angles, speed)

        self.motionService.setCollisionProtectionEnabled("Arms", cp)

    def alignHit(self):
        """Align with the object and play the hit animation after a cue."""
        self.awarenessService.setTrackingMode("WholeBody")

        # wait for confirmation
        self.align()
        self.animate()

        # post animation behaviour

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

        with open("animations/swing1.pickle", "rb") as f:
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

    def isTouched(self, chains):
        """
        Returns True if any of the sensors in the specified chains
        is touched else False.

        Available chains are {"All", "Feet", "Head", "Arms", "LHand", "RHand"}
        """

        parts = [
            "Device/SubDeviceList/Platform/FrontRight/Bumper/Sensor/Value",
            "Device/SubDeviceList/Platform/FrontLeft/Bumper/Sensor/Value",
            "Device/SubDeviceList/Platform/Back/Bumper/Sensor/Value",
            "Device/SubDeviceList/Head/Touch/Rear/Sensor/Value",
            "Device/SubDeviceList/Head/Touch/Middle/Sensor/Value",
            "Device/SubDeviceList/Head/Touch/Front/Sensor/Value",
            "Device/SubDeviceList/LHand/Touch/Back/Sensor/Value",
            "Device/SubDeviceList/RHand/Touch/Back/Sensor/Value"
        ]

        p = []

        for c in chains:
            if c == "All":
                p = parts
                break
            elif c == "Feet":
                p += parts[:3]
            elif c == "Head":
                p += parts[3:6]
            elif c == "Arms":
                p += parts[6:]
            elif c == "LHand":
                p += [parts[6]]
            elif c == "RHand":
                p += [parts[7]]

        return sum(self.memoryService.getListData(p)) > 0

    def holdPose(self, poseName, speed, chains):
        """
        Stays in specified pose until one of the sensors in the chains is touched.
        """
        cp = self.motionService.getCollisionProtectionEnabled("Arms")
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.postureService.goToPosture(poseName, speed)

        while not self.postureService._isRobotInPosture(poseName, 26, 2):
            continue

        while not self.isTouched(chains):
            angles = self.motionService.getAngles("Body", True)
            self.motionService.setAngles("Body", angles, speed)

        self.motionService.setCollisionProtectionEnabled("Arms", cp)


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
