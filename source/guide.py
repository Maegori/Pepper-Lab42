"""
FILE: guide.py
AUTHORS: Lex Johan, Niels Rouws
EMAIL: lex.johan@student.uva.nl, niels.rouws@student.uva.nl
DATE: 25/10/2020

DESCRIPTION: 


NOTES:   
    - "All" and "Move" deactivation of the ExternalCollisionProtection 
        need to be allowed by the owner in the advanced settings
    - Pepper can pull the arm/elbow back down if the time between setAngles()
        calls is too long.
    - Certain AutonomousLife functions can be enabled but be mindful of
        the performance impact because of the aforementioned problem.  
"""

import qi
import argparse
import math


class Behaviour(object):
    """
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

        # Start behaviour
        print("Starting behaviour.")
        self.main()

    def main(self):
        """Move pepper using the combination of the hand, wrist, and elbow as controller."""
        self.motionService.wakeUp()
        self.motionService.moveInit()
        config = self.setSettings()

        # Define waiting & walking pose.
        angles = [-0.25, 0.2, -1.5, 0, 0, 0.4]
        times = [1.5, 1.5, 1.5, 1.5, 1.5, 1.5]
        stiffnesses = [0.6, 0.1, 0, 0, 0, 0]
        speed = 0.1
        turnthold = 0.45

        print("Waiting for partner...")
        self.holdCustomPose("LArm", angles, speed, ["LHand"], False)

        print("Moving by hand.")
        while not self.isTouched(["Feet", "Head"]):
            self.motionService.setAngles("LArm", angles, speed)
            self.motionService.setStiffnesses("LArm", stiffnesses)
            v = self.anglesToMovement(0.6, 14.5, 60)

            if v:
                _, theta, x = v

                if not -turnthold < theta < turnthold:
                    x = 0

                self.motionService.moveToward(x, 0, theta)
            else:
                self.motionService.stopMove()

        print("Exiting guided movement.")
        self.motionService.stopMove()
        self.resetSettings(config)
        self.motionService.rest()

    def holdCustomPose(self, chain, angles, speed, triggers, protection=True):
        """Stays in specified costum pose until one of the sensors in the chains is touched."""

        aa = self.lifeService.getAutonomousAbilityEnabled(
            "BackgroundMovement")
        cp = self.motionService.getCollisionProtectionEnabled("Arms")
        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", False)
        self.motionService.setCollisionProtectionEnabled("Arms", protection)
        print("Trying to reach posture...")

        margin = 0.2

        while True:
            self.motionService.setAngles(chain, angles, speed)
            current = self.motionService.getAngles(chain, True)
            if sum([(y-x)**2 for x, y in zip(current, angles)]) < margin:
                break

        print("Waiting in posture...")
        while not self.isTouched(triggers):
            continue

        print("Posture off.")
        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", aa)
        self.motionService.setCollisionProtectionEnabled("Arms", cp)

    def anglesToMovement(self, threshold, wristDzn, elbowDzn):
        """
        Return the moving parameters based on the positions
        of the hand, wrist and elbow.

        threshold: Decides how far the hand needs to be opened until
        the wrist and elbow are measured.
        wristDzn, elbowDzn are the deadzones in both directions from the
        zero point of the joints.

        Joint information:
        http://doc.aldebaran.com/2-0/family/juliette_technical/joints_juliette.html 
        """
        angles = self.motionService.getAngles("LArm", True)
        hand = angles[5]

        if hand < threshold:
            return []

        # Radians to degrees conversion factor
        c = 180 / math.pi
        wrist = c * angles[4]
        wrist = -round(wrist / 104.5, 1) if not (-wristDzn <
                                                 wrist < wristDzn) else 0.0

        elbow = -angles[3] * c - .5
        elbow = round(1 - (elbow / elbowDzn), 1) if elbow < elbowDzn else 0.0

        return hand, wrist, elbow

    def isTouched(self, chains):
        """
        Returns True if any of the sensors in the specified chains
        is touched otherwise False is returned.

        Available chains are: "All", "Feet", "Head", "Arms", "LHand", "RHand"

        Pepper Actuator and Sensors:
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

    def setSettings(self):
        """Return the current configuration and put Pepper in the configuration to walk hand in hand."""
        ecp = self.motionService.getExternalCollisionProtectionEnabled("All")
        ss = self.motionService.getSmartStiffnessEnabled()
        cp = self.motionService.getCollisionProtectionEnabled("Arms")
        aa = self.lifeService.getAutonomousAbilityEnabled("BackgroundMovement")
        sd = self.awarenessService.isStimulusDetectionEnabled("Touch")
        im = self.motionService.getIdlePostureEnabled("Arms")
        bm = self.motionService.getBreathEnabled("Arms")

        self.motionService.setExternalCollisionProtectionEnabled("All", False)
        self.motionService.setSmartStiffnessEnabled(False)
        self.motionService.setCollisionProtectionEnabled("Arms", False)
        self.lifeService.setAutonomousAbilityEnabled(
            "BackgroundMovement", False)
        self.awarenessService.setStimulusDetectionEnabled("Touch", False)
        self.motionService.setIdlePostureEnabled("Arms", False)
        self.motionService.setBreathEnabled("Arms", False)
        self.awarenessService.pauseAwareness()

        return ecp, ss, cp, aa, sd, im, bm

    def resetSettings(self, config):
        """Reset Pepper in the original configuration."""
        ecp, ss, cp, aa, sd, im, bm = config

        self.motionService.setExternalCollisionProtectionEnabled("All", ecp)
        self.motionService.setSmartStiffnessEnabled(ss)
        self.motionService.setCollisionProtectionEnabled("Arms", cp)
        self.lifeService.setAutonomousAbilityEnabled("BackgroundMovement", aa)
        self.awarenessService.setStimulusDetectionEnabled("Touch", sd)
        self.motionService.setIdlePostureEnabled("Arms", im)
        self.motionService.setBreathEnabled("Arms", bm)
        self.awarenessService.resumeAwareness()


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
