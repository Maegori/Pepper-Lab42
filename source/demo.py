
import qi
import argparse
import functools
import sys
import time
import pickle
import numpy as np
import struct

from pynput import keyboard


MID_FRONT = 8
DETECTION_RANGE = 1.5
TARGET_DISTANCE = 0.42

A_BUTTON_ON = 65537
A_BUTTON_OFF = 65536

B_BUTTON_ON = 16842753
B_BUTTON_OFF = 16842752

EVENT_FORMAT = str('llHHi')
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

PATH = "/dev/input/js0"
SIZE = 100

X = [50495398]
Y = [67272614]


class Navigator(object):

    def __init__(self, app):
        super(Navigator, self).__init__()
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

        # Movement fields
        self.x = 0
        self.theta = 0
        self.listener = None

        # Run behaviour
        self.remoteControlled()

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

    def onPress(self, key):
        """Keyboard controls"""
        x, theta = self.x, self.theta
        speed = 1

        if key == keyboard.Key.up:
            self.x = speed
        elif key == keyboard.Key.down:
            self.x = -speed
        elif key == keyboard.Key.right:
            self.theta = -speed
        elif key == keyboard.Key.left:
            self.theta = speed

        if self.x != x or self.theta != theta:
            print(
                "[MOVING] -- {}, {}".format(self.x, self.theta)
            )
            self.motionService.moveToward(self.x, 0, self.theta)

    def onRelease(self, key):
        """Keyboard controls"""
        x, theta = self.x, self.theta

        if key == keyboard.Key.down or key == keyboard.Key.up:
            self.x = 0
        if key == keyboard.Key.right or key == keyboard.Key.left:
            self.theta = 0

        if not self.x and not self.theta:
            self.motionService.stopMove()
        if self.x != x or self.theta != theta:
            self.motionService.moveToward(self.x, 0, self.theta)

        if key == keyboard.Key.space:
            self.motionService.stopMove()
            self.listener.stop()
            self.remoteControlled()
        if key == keyboard.Key.esc:
            print("Exiting remote controlled mode")
            self.motionService.stopMove()
            self.listener.stop()
            return False

    def remoteControlled(self):
        """Controller controls"""
        arms = set(["LArm", "RArm"])

        self.motionService.wakeUp()
        # self.motionService.setOrthogonalSecurityDistance(0.1)
        self.motionService.setCollisionProtectionEnabled("Arms", False)
        self.motionService.setExternalCollisionProtectionEnabled("Arms", False)
        self.awarenessService.setTrackingMode("WholeBody")
        self.motionService.moveInit()

        print("start")

        with open(PATH, 'rb')as f:
            for i in range(6):
                struct.unpack(EVENT_FORMAT, f.read(EVENT_SIZE))

            while True:
                data = struct.unpack(EVENT_FORMAT, f.read(EVENT_SIZE))

                if data[4] < 50528251 and data[4] > 50462730:
                    X.append(data[4])
                    Y.append(Y[-1])

                    x = round(float(X[-1] - 50495398) / 32678, 1)
                    y = round(float(Y[-1] - 67272614) / 32678, 1)

                    x = 1 + x if x < 0 else x - 1
                    y = -(y + 1) if y < 0 else 1 - y

                    print(round(x, 2), round(y, 2))
                    self.motionService.moveToward(
                        round(y, 2), 0, round(-x / 2, 2))

                elif data[4] < 67305465 and data[4] > 67239936:
                    Y.append(data[4])
                    X.append(X[-1])

                    x = round(float(X[-1] - 50495398) / 32678, 1)
                    y = round(float(Y[-1] - 67272614) / 32678, 1)

                    x = 1 + x if x < 0 else x - 1
                    y = -(y + 1) if y < 0 else 1 - y

                    print(round(x, 2), round(y, 2))
                    self.motionService.moveToward(
                        round(y, 2), 0, round(-x / 2, 2))
                elif data[4] == A_BUTTON_ON or data[4] == A_BUTTON_OFF:
                    self.motionService.stopMove()
                    self.alignHit()
                elif data[4] == B_BUTTON_ON or data[4] == B_BUTTON_OFF:
                    self.motionService.stopMove()
                    self.motionService.rest()
                    break

        # print("Start")
        # # Blocking
        # with keyboard.Listener(
        #     on_press=self.onPress,
        #     on_release=self.onRelease
        # ) as self.listener:
        #     self.listener.join()

        # # Non-blocking
        # self.listener = keyboard.Listener(
        #     on_press=self.onPress,
        #     on_release=self.onRelease
        # )
        # self.listener.start()

        # self.motionService.setExternalCollisionProtectionEnabled("All", True)
        # self.motionService.setCollisionProtectionEnabled("Arms", True)
        # self.motionService.setOrthogonalSecurityDistance(0.4)
        # self.awarenessService.setTrackingMode("MoveContextually")

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

            # if d > DETECTION_RANGE:
            #     self.motionService.stopMove()
            #     return searchflag?

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
    nav = Navigator(app)
    app.run()


# Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value
# Device/SubDeviceList/Pla`tform/Back/Sonar/Sensor/Value
