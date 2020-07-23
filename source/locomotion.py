
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
        self.laserService = session.service("ALLaser")
        # Subscribe to events
        # self.sonarLeft = self.memoryService.subscriber("SonarLeftDetected")
        # self.sonarRight = self.memoryService.subscriber("SonarRightDetected")

        # # Connect event callback
        # self.event = self.sonarLeft.signal.connect(functools.partial(self.log, "SonarLeftDetected"))
        #print("\n".join(self.memoryService.getDataListName()))  
        self.x = 0
        self.theta = 0        
        self.remoteControlled()

    # def move(self):
    #     print("Starting to move")
    #     self.motionService.wakeUp()
    #     self.motionService.moveToward(0, 0, 1)
    #     time.sleep(2)
    #     self.motionService.stopMove()
    #     print("Stopped moving")

    # def follow(self):
    #     print("Following")
        
    #     while True:
    #         if (self.memoryService.getData("Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value") > 1):
    #             self.motionService.moveToward(0, 0, 1)
    #             time.sleep(3)
            
    #         self.motionService.stopMove()

    def on_press(self, key):
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

    def on_release(self, key):
        if keyboard.Key.down or keyboard.Key.up:
            self.x = 0 
        if keyboard.Key.right or keyboard.Key.left:
            self.theta = 0

        print(self.x, self.theta)
        if not self.x and not self.theta:
            self.motionService.stopMove()   



        if key == keyboard.Key.esc:
            print("Exiting remote controlled mode")
            self.motionService.stopMove()  
            return False

    def remoteControlled(self):
        self.motionService.wakeUp()
        self.motionService.moveInit()
        print("Start")

        # Blocking
        with keyboard.Listener(on_press =self.on_press, on_release=self.on_release) as listener:
            listener.join()

        # # Non-blocking 
        # listener = keyboard.Listener(
        #     on_press=on_press,
        #     on_release=on_release)
        # listener.start()

        print("Stop")
        self.motionService.rest()
        return
        
        

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
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    print("Succesfully connected to Pepper @ tcp://" + args.ip + ":" + str(args.port))
    nav = Navigator(app)
    app.run()


# Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value
# Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value