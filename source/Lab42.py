"""
"""


import qi
import qicore
import argparse
import functools
import sys
import time
import io
import struct
import math
import threading
import pickle
import time

import numpy as np
from xbone import Xbone

MID_FRONT = 8
DETECTION_RANGE = 1.5
TARGET_DISTANCE = 0.4
DEADZONE = 0.2
COEFF = 180 / math.pi  # Radians to degrees conversion factor


class Lab42(object):
    """
    """

    def __init__(self, app):
        """
        """
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
        self.tabletService = session.service("ALTabletService")

        # Set subscriptions
        self.touch = self.memoryService.subscriber("TouchChanged")
        self.block = self.memoryService.subscriber(
            "ALMotion/MoveFailed"
        )
        self.push = self.memoryService.subscriber("ALMotion/RobotPushed")
        self.pushrec = self.memoryService.subscriber(
            "ALMotion/Safety/PushRecovery")
        self.fall = self.memoryService.subscriber("ALMotion/RobotIsFalling")
        self.fall1 = self.memoryService.subscriber("robotHasFallen")
        self.slope = self.memoryService.subscriber(
            "ALMotion/Safety/RobotOnASlope")

        # Connect callbacks
        self.id = self.touch.signal.connect(
            functools.partial(self.onTouched, "TouchChanged")
        )
        self.block.signal.connect(
            functools.partial(self.onBlocked, "ALMotion/MoveFailed")
        )
        self.push.signal.connect(
            functools.partial(self.onPushed, "ALMotion/RobotPushed")
        )
        self.pushrec.signal.connect(
            functools.partial(self.onRecovery, "ALMotion/Safety/PushRecovery")
        )
        self.fall.signal.connect(
            functools.partial(self.onFall, "ALMotion/RobotIsFalling")
        )
        self.fall1.signal.connect(
            functools.partial(self.onFallen, "robotHasFallen"))

        self.slope.signal.connect(
            functools.partial(self.onSlope, "ALMotion/Safety/RobotOnASlope")
        )

        # TTS settings
        self.tts.setLanguage("Dutch")
        self.tts.setParameter("pitchShift", 1.1)
        self.tts.setParameter("speed", 90)

        # Input handling
        self.running = True
        self.controller = Xbone('/dev/input/js0')

        # speech handling
        self.talking = True

        # Run behaviour
        self.demo()

    def resetSettings(self):
        """
        """

        stimuli = ["People", "Touch", "TabletTouch",
                   "Sound", "Movement", "NavigationMotion"]

        # Motion service
        self.motionService.setExternalCollisionProtectionEnabled("All", True)
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.motionService.setSmartStiffnessEnabled(False)
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
        # Idle and breath animation
        self.motionService.setIdlePostureEnabled("Arms", True)
        self.motionService.setBreathEnabled("Arms", False)

    def demo(self):
        """Main control loop."""

        stimuli = ["People", "Touch", "TabletTouch",
                   "Sound", "Movement", "NavigationMotion"]
        print("Starting Demo.")
        self.resetSettings()
        for s in stimuli:
            self.awarenessService.setStimulusDetectionEnabled(s, False)

        self.motionService.wakeUp()
        self.motionService.moveInit()

        self.tabletService.showWebview(
            "http://198.18.0.1/apps/boot-config/preloading_dialog.html")

        t = threading.Thread(target=self.controller.read)
        t.deamon = True
        t.start()

        speech = threading.Thread(target=self.talk)
        speech.daemon = True
        speech.start()

        while self.running:
            time.sleep(0.001)
            self.handleEvents()

        print("Closing App.")
        self.resetSettings()
        self.tabletService.hideWebview()
        # Wrm ervoor gekozen de resetsettings aan te passen?

    def handleEvents(self):
        """
        """
        x = -self.controller.request_axis('ry')
        theta = -self.controller.request_axis('rx')

        if -DEADZONE < x < DEADZONE:
            x = 0
        if -DEADZONE < theta < DEADZONE:
            theta = 0

        if not -0.45 < theta < 0.45:
            x = 0

        self.motionService.moveToward(x, 0, theta)

        if self.controller.request_button("tr") or self.controller.request_button("tl"):
            self.motionService.stopMove()
        elif self.controller.request_button('a'):
            self.alignHit()
            self.motionService.stopMove()
        elif self.controller.request_button('y'):
            self.motionService.stopMove()
            self.guidedMove()
        elif self.controller.request_button('select'):
            self.motionService.stopMove()
            self.running = False
            self.talking = False
            self.controller.terminate()

    def guidedMove(self):
        """
        """
        ecp = self.motionService.getExternalCollisionProtectionEnabled("All")
        self.motionService.setExternalCollisionProtectionEnabled("All", False)

        ss = self.motionService.getSmartStiffnessEnabled()
        self.motionService.setSmartStiffnessEnabled(False)

        tm = self.awarenessService.getTrackingMode()
        # self.awarenessService.setTrackingMode("Head")

        cp = self.motionService.getCollisionProtectionEnabled("Arms")
        self.motionService.setCollisionProtectionEnabled("Arms", False)

        aa = self.lifeService.getAutonomousAbilityEnabled(
            "BackgroundMovement")
        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", False)

        sd = self.awarenessService.isStimulusDetectionEnabled("Touch")
        self.awarenessService.setStimulusDetectionEnabled("Touch", False)

        im = self.motionService.getIdlePostureEnabled("Arms")
        self.motionService.setIdlePostureEnabled("Arms", False)

        bm = self.motionService.getBreathEnabled("Arms")
        self.motionService.setBreathEnabled("Arms", False)

        print("Guided mode active.")

        self.motionService.moveInit()

        angles = [-0.25, 0.2, -1.5, 0, 0, 0.4]
        times = [1.5, 1.5, 1.5, 1.5, 1.5, 1.5]

        speed = 0.1

        print("Waiting for partner...")
        self.holdCustomPose("LArm", angles, speed, ["LHand"])
        print("Moving by Hand.")

        while not self.controller.request_button("b"):
            self.motionService.setAngles(
                "LArm", angles, speed)
            self.motionService.setStiffnesses(
                "LArm", [0.6, 0.1, 0, 0, 0, 0])
            v = self.anglesToMovement()

            if v:
                x = v[0]
                theta = v[1]

                if not -0.45 < theta < 0.45:
                    x = 0

                self.motionService.moveToward(x, 0, theta)
            else:
                self.motionService.stopMove()

        self.motionService.stopMove()
        print("\nExiting guided movement.")

        self.postureService.goToPosture("Stand", 0.3)
        self.motionService.setExternalCollisionProtectionEnabled("All", ecp)
        self.motionService.setCollisionProtectionEnabled("Arms", cp)

        self.awarenessService.setStimulusDetectionEnabled("Touch", sd)
        # self.awarenessService.setTrackingMode(tm)
        self.motionService.setSmartStiffnessEnabled(ss)
        self.motionService.setExternalCollisionProtectionEnabled("All", ecp)
        self.motionService.setIdlePostureEnabled("Arms", im)
        self.motionService.setBreathEnabled("Arms", bm)

        print("Standing around.")

    def anglesToMovement(self):
        angles = self.motionService.getAngles("LArm", True)

        hand = angles[5]

        if hand < 0.6:
            return []

        theta = 60.0
        elbow = -angles[3] * COEFF - .5
        elbow = round(1 - (elbow / theta), 1) if elbow < theta else 0.0

        theta = 14.5
        wrist = angles[4] * COEFF
        wrist = -round(wrist / 104.5, 1) if not (-theta <
                                                 wrist < theta) else 0.0

        return elbow, wrist, hand

    def handToScalar(self):
        """
        """
        return self.motionService.getAngles("LArm", True)[5]

    def elbowToScalar(self):
        """
        """
        e_angle = -self.motionService.getAngles("LArm", True)[3] * COEFF
        e_angle -= 0.5
        theta = 60.0

        if e_angle < theta:
            return round(1 - (e_angle / theta), 1)
        else:
            return 0.0

    def wristToScalar(self):
        """
        """
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

        ecp = self.motionService.getExternalCollisionProtectionEnabled("All")
        self.motionService.setExternalCollisionProtectionEnabled("All", False)

        print("Waiting for confirmation to align and hit.")
        angles_1 = [0.80, -0.29, 1.61, 1.05, 1.55, 1]  # unused parameter?
        angles_2 = [0.80, -0.29, 1.61, 1.05, 1.55, 0]
        speed = 0.1

        self.motionService.closeHand("RHand")
        self.postureService.goToPosture("Stand", 0.2)
        self.align()
        self.animate()

        print("Waiting for confirmation to release the hammer.")
        self.motionService.moveToward(0, 0, -1)
        time.sleep(1.1)
        self.motionService.stopMove()
        self.holdCustomPose(
            "RArm",
            angles_2,
            speed,
            ["RHand"],
            False
        )
        self.motionService.openHand("RHand")
        self.postureService.goToPosture("Stand", 0.2)
        self.awarenessService.setTrackingMode(tm)
        self.motionService.setExternalCollisionProtectionEnabled("All", ecp)

    def align(self):
        """
        """
        self.motionService.moveInit()

        keys = [
            "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg" +
            ("0" if i < 10 else "") + str(i) + "/X/Sensor/Value" for i in range(1, 16)
        ]

        phi = 0.0698  # Radians between two adjacent lasers

        while not self.controller.request_button("b"):
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

        with open("animations/swing2.pickle", "rb") as f:
            animation = pickle.load(f)

        for key in animation.keys():
            names.append(key)
            times.append(animation[key][0])
            keys.append(animation[key][1])

        self.postureService.goToPosture("StandInit", 1)
        self.motionService.angleInterpolation(names, keys, times, isAbsolute)
        self.motionService.setExternalCollisionProtectionEnabled("Arms", ecp)

    def approach(self, keys):
        """Move closer until the object is in the target range."""
        self.motionService.setOrthogonalSecurityDistance(0.2)
        self.motionService.setTangentialSecurityDistance(0.05)

        print("Approaching target")
        scan = self.memoryService.getListData(keys)

        while min(scan) > TARGET_DISTANCE or not self.controller.request_button("b"):
            self.motionService.moveToward(0.3, 0, 0)
            scan = self.memoryService.getListData(keys)

        self.motionService.stopMove()
        print("In range of target")
        self.motionService.setOrthogonalSecurityDistance(0.4)
        self.motionService.setTangentialSecurityDistance(0.1)
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
        while not self.postureService.goToPosture(poseName, speed) or not self.controller.request_button("b"):
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
        while not self.controller.request_button("b"):
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

    def isTouched(self, chains):
        """
        Returns True if any of the sensors in the specified chains
        is touched else False.

        Available chains are: {"All", "Feet", "Head", "Arms", "LHand", "RHand"}
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

    def talk(self):
        """
        Function to control the Text-to-Speech with either
        preprogrammed or costum voice lines.
        """

        lines = [
            "Dit is allemaal heel interessant, maar ik kan niet wachten" +
            "totdat de bouw gaat beginnen!" +
            "\\pau=800\\" +
            "Ik wil daarom nu de eerste paal gaan slaan." +
            "\\pau=800\\" +
            "Gaan jullie mee?",

            "Ja\\emph=200\\, Ik krijg inderdaad mijn eigen robotlab.",

            "Ik ga zelf leren op afstand koorts te meten, dat is handig" +
            "bij bijvoorbeeld een Coronacrisis," +
            "\\pau=600\\" +
            "en de \\toi=lhp\\n`@Ou\\toi=orth\\ robots zijn natuurlijk aan het trainen" +
            "voor het wereldkampioenschap voetbal." +
            "\\pau=1000\\" +
            "Maar bovenop dat hele nieuwe robotlab komt het hele Lab42," +
            "vol met innovatie." +
            "\\pau=800\\" +
            "En dat lab moet wel snel gebouwd worden." +
            "\\pau=500\\" +
            "Dus kom, laten we de eerste paal gaan slaan!",

            "De eerste paal is geslagen, laat de bouw beginnen!"

        ]

        while self.talking:
            line = str(raw_input("Say: ")).strip()
            if line == '':
                continue
            elif line[0] == '~':
                if line == 'h' or line == "help":
                    for i, x in enumerate(lines):
                        print("["+str(i)+"] : " + x)
                else:
                    try:
                        x = int(line[1:])
                        line = lines[x]
                    except:
                        print("Given index is invalid.")
                        continue

            c = str(raw_input("Are your sure you want to say:\n'" +
                              line + "'\n[y/n]: ")).strip().lower()

            if c == 'y':
                self.tts.say(line)

    def onTouched(self, strVarName, value):
        """
        """
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

    def onBlocked(self, strVarName, value):
        """Print information when movement is blocked."""

        print(
            "[FAIL] -- CAUSE={}, STATUS={}, LOCATION={}"
            .format(value[0], value[1], value[2])
        )

    def onPushed(self, str, val):
        print("[WARNING] -- Pepper was pushed.")

    def onRecovery(self, str, val):
        print("[WARNING] -- Push recovery active.")

    def onFall(self, str, val):
        print("[WARNING] -- Pepper is falling.")

    def onFallen(self, str, val):
        print("[WARNING] -- Pepper has fallen down.")

    def onSlope(self, str, val):
        print("[WARNING] -- Pepper is on a slope.")


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
