import qi
import argparse
import time
import math
import sys
import functools


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
        self.id = self.touch.signal.connect(functools.partial(self.onTouched, "TouchChanged"))

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
        
        self.id = self.touch.signal.connect(functools.partial(self.onTouched, "TouchChanged"))

    def move(self):
        print("Moving")
        self.postureService.goToPosture("StandZero", 0.5)
        # print(self.postureService.goToPosture("walkByHand", 0.5))
        self.motionService.moveInit()
        # self.awarenessService.setTrackingMode("Head")
        self.motionService.setCollisionProtectionEnabled("Arms", False)
        self.motionService.setExternalCollisionProtectionEnabled("All", False)
        

        print("Moooo")
        #self.motionService.setStiffnesses("LArm", [1, 1, 1, 0, 0, 1])
        # elbow = 3
        # wrist = 4

        # rad_conv = 180 / math.pi

        # print("start")
        # while True:
        #     try:
        #         w_rad = self.motionService.getAngles("LArm", True)[wrist]
        #         self.motionService.moveToward(0, 0, -round((w_rad * rad_conv) / 104.5, 2))
        #     except KeyboardInterrupt:
        #         print("\nstopped")
        #         break

        self.motionService.stopMove()
        self.motionService.setCollisionProtectionEnabled("Arms", True)
        self.motionService.setExternalCollisionProtectionEnabled("All", True)
        #self.awarenessService.setTrackingMode("MoveContextually")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="146.50.60.38",
                        help="Robot IP address. On robot or Local Naoqi: use '146.50.60.38'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--animation", type=str, help="Name of the animation to play")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["Swing", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    print("Succesfully connected to Pepper @ tcp://" + args.ip + ":" + str(args.port))
    j = Joints(app)
    app.run()