import qi
import argparse
import functools
import sys
import time
import io
import struct
import math
import threading
import pickle

import numpy as np
from xbone import Xbone

COEFF = 180 / math.pi
MID_FRONT = 8
DETECTION_RANGE = 1.5
TARGET_DISTANCE = 0.42
DEADZONE = 0.2


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
        self.lifeService = session.service("ALAutonomousLife")
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
        self.demo()

    def resetSettings(self):

        stimuli = ["People", "Touch", "TabletTouch",
                   "Sound", "Movement", "NavigationMotion"]

        # Motion service
        self.motionService.setExternalCollisionProtectionEnabled("All", True)
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.motionService.setSmartStiffnessEnabled(True)
        self.motionService.setOrthogonalSecurityDistance(0.4)  # default
        self.motionService.setTangentialSecurityDistance(0.1)  # default
        # Life Service
        self.lifeService.setState("solitary")  # default
        self.lifeService.setAutonomousAbilityEnabled("All", True)
        # Awareness Service
        self.awarenessService.setEnabled(True)
        self.awarenessService.setTrackingMode("BodyRotation")  # default
        for s in stimuli:
            self.awarenessService.setStimulusDetectionEnabled(s, True)
        self.awarenessService.setEngagementMode("Unengaged")  # default

    def demo(self):
        """Main control loop."""
        print("Starting Demo.")
        self.resetSettings()
        self.motionService.wakeUp()
        self.motionService.moveInit()

        ecp = self.motionService.getExternalCollisionProtectionEnabled("All")
        self.motionService.setExternalCollisionProtectionEnabled("All", False)

        t = threading.Thread(target=self.controller.read)
        t.deamon = True
        t.start()

        while self.running:
            time.sleep(0.001)
            self.handleEvents()

        print("Closing App.")
        self.motionService.setExternalCollisionProtectionEnabled("All", ecp)
        self.resetSettings()
        self.motionService.rest()
        sys.exit(0)

    def handleEvents(self):
        x = -self.controller.request_axis('ry')
        theta = -self.controller.request_axis('rx')

        if -DEADZONE < x < DEADZONE:
            x = 0
        if -DEADZONE < theta < DEADZONE:
            theta = 0

        self.motionService.moveToward(x, 0, theta)

        if self.controller.request_button("tr") or self.controller.request_button("tl"):
            self.motionService.stopMove()
        elif self.controller.request_button('a'):
            self.alignHit()
            self.motionService.stopMove()
        elif self.controller.request_button('y'):
            self.guidedMove()
            self.motionService.stopMove()
        elif self.controller.request_button('select'):
            self.motionService.stopMove()
            self.motionService.rest()
            self.running = False

    def guidedMove(self):
        ss = self.motionService.getSmartStiffnessEnabled()
        self.motionService.setSmartStiffnessEnabled(False)

        tm = self.awarenessService.getTrackingMode()
        self.awarenessService.setTrackingMode("Head")

        cp = self.motionService.getCollisionProtectionEnabled("Arms")
        self.motionService.setCollisionProtectionEnabled("Arms", False)

        ecp = self.motionService.getExternalCollisionProtectionEnabled("All")
        self.motionService.setExternalCollisionProtectionEnabled("All", False)

        aa = self.lifeService.getAutonomousAbilityEnabled(
            "BackgroundMovement")
        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", False)

        sd = self.awarenessService.isStimulusDetectionEnabled("Touch")
        self.awarenessService.setStimulusDetectionEnabled("Touch", False)

        print("Guided mode active.")

        self.motionService.moveInit()

        angles = [-0.25, 0.2, -1.5, 0, 0, 0.4]
        speed = 0.1

        print("Waiting for partner...")
        self.holdCustomPose("LArm", angles, speed, ["LHand"])
        print("Moving by Hand.")
        while True:
            try:
                self.motionService.setAngles(
                    "LArm", angles, speed)
                self.motionService.setStiffnesses(
                    "LArm", [0.6, 0.1, 0, 0, 0, 0])
                if self.handToScalar() > 0.6:
                    self.motionService.moveToward(
                        self.elbowToScalar(), 0, self.wristToScalar())
                else:
                    self.motionService.stopMove()

            except KeyboardInterrupt:
                self.motionService.stopMove()
                print("\nExiting guided movement.")
                break

        self.postureService.goToPosture("Stand", 0.3)
        self.motionService.setExternalCollisionProtectionEnabled("All", ecp)
        self.motionService.setCollisionProtectionEnabled("Arms", cp)

        self.awarenessService.setStimulusDetectionEnabled("Touch", sd)
        self.awarenessService.setTrackingMode(tm)
        self.motionService.setSmartStiffnessEnabled(ss)
        print("Standing around.")

    def handToScalar(self):
        return self.motionService.getAngles("LArm", True)[5]

    def elbowToScalar(self):
        e_angle = -self.motionService.getAngles("LArm", True)[3] * COEFF
        e_angle -= 0.5
        theta = 60.0

        if e_angle < theta:
            return round(1 - (e_angle / theta), 1)
        else:
            return 0.0

    def wristToScalar(self):
        w_angle = self.motionService.getAngles("LArm", True)[4] * COEFF
        theta = 14.5
        if not (-theta < w_angle < theta):
            return -round(w_angle / 104.5, 1)
        else:
            return 0.0

    def alignHit(self):
        """Align with the object and play the hit animation after a cue."""
        tm = self.awarenessService.getTrackingMode()
        self.awarenessService.setTrackingMode("Head")

        print("Waiting for confirmation to align and hit.")
        angles = [0.80, -0.29, 1.61, 1.05, 1.55, 0]
        speed = 0.1

        self.holdCustomPose(
            "RArm",
            angles,
            speed,
            ["RHand"],
            False
        )
        self.postureService.goToPosture("Stand", 0.5)
        self.align()
        self.animate()

        print("Waiting for confirmation to release the hammer.")
        self.motionService.moveToward(0, 0, -1)
        time.sleep(1.1)
        self.motionService.stopMove()
        self.holdCustomPose(
            "RArm",
            angles,
            speed,
            ["RHand"],
            False
        )
        self.postureService.goToPosture("Stand", 0.5)
        self.awarenessService.setTrackingMode(tm)

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
        ecp = self.motionService.getExternalCollisionProtectionEnabled("Arms")
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

    def holdPose(self, poseName, speed, chains, protection=True):
        """
        Stays in specified pose until one of the sensors in the chains is touched.
        """
        aa = self.lifeService.getAutonomousAbilityEnabled(
            "BackgroundMovement")
        cp = self.motionService.getCollisionProtectionEnabled("Arms")

        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", False)
        self.motionService.setCollisionProtectionEnabled("Arms", protection)

        print("Trying to reach posture...")
        while not self.postureService.goToPosture(poseName, speed):
            continue

        angles = self.motionService.getAngles("Body", True)
        self.motionService.setAngles("Body", angles, speed)

        print("Waiting in posture.")
        while not self.isTouched(chains):
            continue

        print("Posture off.")
        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", aa)
        self.motionService.setCollisionProtectionEnabled("Arms", cp)

    def holdCustomPose(self, chain, angles, speed, triggers, protection=True):
        """
        Stays in specified pose until one of the sensors in the chains is touched.
        """
        aa = self.lifeService.getAutonomousAbilityEnabled(
            "BackgroundMovement")
        cp = self.motionService.getCollisionProtectionEnabled("Arms")

        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", False)
        self.motionService.setCollisionProtectionEnabled("Arms", protection)

        print("Trying to reach posture...")
        while True:
            self.motionService.setAngles(chain, angles, speed)
            current = self.motionService.getAngles(chain, True)
            if sum([(y-x)**2 for x, y in zip(current, angles)]) < 0.2:
                break

        print("Waiting in posture...")
        while not self.isTouched(triggers):
            continue

        print("Posture off.")
        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", aa)
        self.motionService.setCollisionProtectionEnabled("Arms", cp)

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
            else:
                raise KeyError

        return sum(self.memoryService.getListData(p)) > 0


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
