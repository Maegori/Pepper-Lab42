
import qi
import argparse
import functools
import sys
import time

from pynput import keyboard


class Navigator(object):

    def __init__(self, app):
        super(Navigator, self).__init__()
        app.start()
        session = app.session

        # Get services
        self.memoryService = session.service("ALMemory")
        self.motionService = session.service("ALMotion")
        self.postureService = session.service("ALRobotPosture")
        self.lifeService = session.service("ALAutonomousLife")
        self.tts = session.service("ALTextToSpeech")

        # Set subscriptions
        self.touch = self.memoryService.subscriber("TouchChanged")
        self.id = self.touch.signal.connect(
            functools.partial(self.onTouched, "TouchChanged"))

        # Fields
        self.language = "Dutch"
        self.x = 0
        self.theta = 0

        # Run behaviour
        self.remoteControlled()

    def onTouched(self, strVarName, value):
        # self.touch.signal.disconnect(self.id)

        arms = set(["LArm", "RArm"])
        parts = set()

        for p in value:
            if p[1]:
                parts.add(p[0])
            elif p[0] in arms:
                self.motionService.setStiffnesses(arms, 1)

        if arms.intersection(parts):
            self.tts.say("Bla")
            self.motionService.setStiffnesses(arms, 0)

        # self.id = self.touch.signal.connect(
        #     functools.partial(self.onTouched, "TouchChanged"))

    def onPress(self, key):
        x, theta = self.x, self.theta

        if key == keyboard.Key.up:
            self.x = 1
        elif key == keyboard.Key.down:
            self.x = -1
        elif key == keyboard.Key.right:
            self.theta = -1
        elif key == keyboard.Key.left:
            self.theta = 1

        if self.x != x or self.theta != theta:
            print("Moving: ", self.x, self.theta)
            self.motionService.moveToward(self.x, 0, self.theta)

    def onRelease(self, key):
        x, theta = self.x, self.theta

        if key == keyboard.Key.down or key == keyboard.Key.up:
            self.x = 0
        if key == keyboard.Key.right or key == keyboard.Key.left:
            self.theta = 0

        print(key, self.x, self.theta)

        if not self.x and not self.theta:
            print("Stopping")
            self.motionService.stopMove()
        if self.x != x or self.theta != theta:
            self.motionService.moveToward(self.x, 0, self.theta)

        if key == keyboard.Key.esc:
            print("Exiting remote controlled mode")
            self.motionService.stopMove()
            return False

    def remoteControlled(self):
        self.motionService.wakeUp()
        self.lifeService.setAutonomousAbilityEnabled("All", False)
        self.motionService.moveInit()
        print("Start")

        # Blocking
        with keyboard.Listener(on_press=self.onPress, on_release=self.onRelease) as listener:
            listener.join()

        # # Non-blocking
        # listener = keyboard.Listener(
        #     on_press=on_press,
        #     on_release=on_release)
        # listener.start()

        print("Stop")
        self.lifeService.setAutonomousAbilityEnabled("All", True)


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
