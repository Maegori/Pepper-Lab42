
import qi
import argparse
import functools
import sys
import time
import io
import struct
import math

EVENT_FORMAT = str('llHHi')
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

PATH = "/dev/input/js0"

X = [50495398]
Y = [67272614]

#from pynput import keyboard

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

        self.move()

    def move(self):
        self.motionService.wakeUp()
        self.motionService.moveInit()
        print("Start")

        with open(PATH, 'rb')as f:
            for i in range(6):
                struct.unpack(EVENT_FORMAT, f.read(EVENT_SIZE))

            while True:
                data = struct.unpack(EVENT_FORMAT, f.read(EVENT_SIZE))
                if data[4] < 50528251 and data[4] > 50462720:
                    X.append(data[4])
                    Y.append(Y[-1])

                    x = round(float(X[-1] - 50495398) / 32678, 1)
                    y = round(float(Y[-1] - 67272614) / 32678, 1)

                    x = 1 + x if x < 0 else x - 1
                    y = -(y + 1) if y < 0 else 1 - y

                    print(round(x, 2), round(y, 2))
                    self.motionService.moveToward(round(y, 2), 0, round(-x, 2))

                elif data[4] < 67305465 and data[4] > 67239936:
                    Y.append(data[4])
                    X.append(X[-1])

                    x = round(float(X[-1] - 50495398) / 32678, 1)
                    y = round(float(Y[-1] - 67272614) / 32678, 1)

                    x = 1 + x if x < 0 else x - 1
                    y = -(y + 1) if y < 0 else 1 - y

                    print(round(x, 2), round(y, 2))
                    self.motionService.moveToward(round(y, 2), 0, round(-x, 2))

    # # def move(self):
    # #     print("Starting to move")
    # #     self.motionService.wakeUp()
    # #     self.motionService.moveToward(0, 0, 1)
    # #     time.sleep(2)
    # #     self.motionService.stopMove()
    # #     print("Stopped moving")

    # # def follow(self):
    # #     print("Following")
        
    # #     while True:
    # #         if (self.memoryService.getData("Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value") > 1):
    # #             self.motionService.moveToward(0, 0, 1)
    # #             time.sleep(3)
            
    # #         self.motionService.stopMove()

    # def on_press(self, key):
    #     if key == keyboard.Key.up:
    #         self.motionService.moveToward(1, 0, 0)
    #     elif key == keyboard.Key.right:
    #         self.motionService.moveToward(0, 0, -1)
    #     elif key == keyboard.Key.down:
    #         self.motionService.moveToward(-1, 0, 0)
    #     elif key == keyboard.Key.left:
    #         self.motionService.moveToward(0, 0, 1)

    # def on_release(self, key):
    #     self.motionService.stopMove()

    #     if key == keyboard.Key.esc:
    #         print("Exiting remote controlled mode")
    #         return False

    # def remoteControlled(self):
    #     self.motionService.wakeUp()
    #     self.motionService.moveInit()
    #     print("Start")

    #     # Blocking
    #     with keyboard.Listener(on_press =self.on_press, on_release=self.on_release) as listener:
    #         listener.join()

    #     # # Non-blocking 
    #     # listener = keyboard.Listener(
    #     #     on_press=on_press,
    #     #     on_release=on_release)
    #     # listener.start()

    #     print("Stop")
    #     self.motionService.rest()
        
        

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
    nav.move()
    app.run()


# Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value
# Device/SubDeviceList/Platform/Back/Sonar/Sensor/Value