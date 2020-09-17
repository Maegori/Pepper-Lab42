import qi
import argparse
import time
import math
import sys
import functools

COEFF = 180 / math.pi


class Joints(object):

    def __init__(self, app):
        super(Joints, self).__init__()
        app.start()
        session = app.session
        self.memoryService = session.service("ALMemory")
        self.awarenessService = session.service("ALBasicAwareness")
        self.motionService = session.service("ALMotion")
        self.postureService = session.service("ALRobotPosture")
        self.lifeService = session.service("ALAutonomousLife")

        self.lifeService.setAutonomousAbilityEnabled("All", False)
        self.touch = self.memoryService.subscriber("TouchChanged")
        self.id = self.touch.signal.connect(
            functools.partial(self.onTouched, "TouchChanged"))

        self.motionService.wakeUp()
        self.frozen = True

        self.move()

    def onTouched(self, strVarName, value):
        self.touch.signal.disconnect(self.id)
        print("touched")

        for p in value:
            if p[1] and p[0] == "LArm":
                self.frozen = False
                return

        self.id = self.touch.signal.connect(
            functools.partial(self.onTouched, "TouchChanged"))

    def move(self):
        print("Moving")

        self.motionService.moveInit()
        self.awarenessService.setTrackingMode("Head")
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.motionService.setExternalCollisionProtectionEnabled("All", False)
        self.awarenessService.resumeAwareness()
        self.awarenessService.setEnabled(True)
        self.awarenessService.setStimulusDetectionEnabled("Touch", False)
        #self.postureService.goToPosture("walkByHand", 0.5)

        self.holdPose("StandZero", 0.5, ["All"])
        print("start")
        while True:
            try:
                self.motionService.setAngles(
                    "LArm", [-0.25, 0.2, -2.0857, 0, 0, 0.4], 0.1)
                self.motionService.setStiffnesses(
                    "LArm", [0.6, 0.1, 0, 0, 0, 0])
                if self.handToScalar() > 0.6:
                    self.motionService.moveToward(
                        self.elbowToScalar(), 0, self.wristToScalar())
                else:
                    self.motionService.stopMove()

            except KeyboardInterrupt:
                print("\nstopped")
                break

        self.motionService.stopMove()
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.motionService.setExternalCollisionProtectionEnabled("All", True)
        self.postureService.goToPosture("Stand", 0.5)
        self.awarenessService.setStimulusDetectionEnabled("Touch", True)
        self.awarenessService.setTrackingMode("MoveBody")

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

        print("Trying to reach posture...")
        while not self.postureService._isRobotInPosture(poseName, 26, 2):
            continue

        print("Posture Reached.")
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
    j = Joints(app)
    app.run()