"""
FILE: approach.py
AUTHORS: Lex Johan, Niels Rouws
EMAIL: lex.johan@student.uva.nl, niels.rouws@student.uva.nl
DATE: 25/10/2020

DESCRIPTION:
    Behaviour class for Pepper robot to approach the closest object in
    the range of the lasers.

NOTES:
    - The behaviour won't fuction well at ranges <0.3 or >2 meters
        results may vary depending on the size of the target object.
    - Avoid reflective or straight wide objects (walls) because Pepper
        will alternate between multiple closest point and reach none.
"""

import qi
import argparse
import time
import pickle


class Behaviour(object):
    """
    Behaviour class for Pepper robot to approach the closest object in
    the range of the lasers.
    """

    def __init__(self, app):
        super(Behaviour, self).__init__()
        app.start()
        session = app.session

        # Get services
        self.memoryService = session.service("ALMemory")
        self.motionService = session.service("ALMotion")
        self.awarenessService = session.service("ALBasicAwareness")
        self.lifeService = session.service("ALAutonomousLife")
        self.postureService = session.service("ALRobotPosture")

        # Fields
        self.keys = [
            "Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg" +
            ("0" if i < 10 else "") + str(i) + "/X/Sensor/Value" for i in range(1, 16)
        ]

        # Start behaviour
        print("Starting behaviour.")
        self.main()

    def main(self):
        """Align with the object and play the hit animation after a cue."""
        self.motionService.wakeUp()
        self.motionService.moveInit()
        tm = self.awarenessService.getTrackingMode()
        self.awarenessService.setTrackingMode("Head")

        if self.align(1.5, 0.4):
            print("Target reached.")
            # Swing animation
            self.motionService.moveToward(0, 0, 0.7)
            time.sleep(1.15)
            self.motionService.stopMove()
            self.animate("animations/swing2.pickle", False)

        self.motionService.stopMove()
        self.awarenessService.setTrackingMode(tm)
        self.motionService.rest()

    def align(self, detectionRange, maxDistance):
        """
        Returns True on succesfull alignment with the object in front else False.
        Alternatly turns and approaches until the closest object is within the maxDistance.
        """

        # Radians between two adjacent lasers
        phi = 0.0698
        middle = 8

        while not self.isTouched(["All"]):
            scan = self.memoryService.getListData(self.keys)
            target = scan.index(min(scan))

            print(
                "Aligning with target:{}\tdistance:{:.2f}".format(
                    target, scan[target])
            )

            if scan[target] < detectionRange:
                if target == middle:
                    self.motionService.stopMove()
                    if self.approach(maxDistance) == middle:
                        return True

                self.motionService.moveToward(
                    0, 0, float((middle - target) * phi))

        self.motionService.stopMove()
        print("Alignment aborted.")
        return False

    def approach(self, distance):
        """
        Returns the laser index pointing at the closest object
        after moving forward until the object is whitin the maximum distance.
        Depending on the speed the security distances can be changed appropriately.

        Pepper security distances:
        http://doc.aldebaran.com/2-5/naoqi/motion/reflexes-external-collision.html 
        """
        self.motionService.setOrthogonalSecurityDistance(0.2)
        self.motionService.setTangentialSecurityDistance(0.05)

        print("Approaching target...")
        scan = self.memoryService.getListData(self.keys)

        while min(scan) > distance and not self.isTouched(["All"]):
            self.motionService.moveToward(0.3, 0, 0)
            scan = self.memoryService.getListData(self.keys)

        self.motionService.stopMove()
        self.motionService.setOrthogonalSecurityDistance(0.4)
        self.motionService.setTangentialSecurityDistance(0.1)
        return scan.index(min(scan))

    def animate(self, file):
        """Go to the "Stand" posture and play the animation in the .pickle file."""
        ecp = self.motionService.getExternalCollisionProtectionEnabled("Arms")
        self.motionService.setExternalCollisionProtectionEnabled(
            "Arms", protection)

        animation = dict()
        names = []
        times = []
        keys = []

        with open(file, "rb") as f:
            animation = pickle.load(f)

        for key in animation.keys():
            names.append(key)
            times.append(animation[key][0])
            keys.append(animation[key][1])

        self.postureService.goToPosture("StandInit", .5)
        self.motionService.angleInterpolation(names, keys, times, True)
        self.motionService.setExternalCollisionProtectionEnabled("Arms", ecp)

    def isTouched(self, chains):
        """
        Returns True if any of the sensors in the list of chains
        is touched otherwise False is returned.

        Available chains are: "All", "Feet", "Head", "Arms", "LHand", "RHand"

        Pepper actuator and sensors:
        http://doc.aldebaran.com/2-0/family/juliette_technical/juliette_dcm/actuator_sensor_names.html
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
    nav = Behaviour(app)
    app.run()
