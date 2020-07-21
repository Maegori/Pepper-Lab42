import qi
import argparse
import functools
import sys
import time
import matplotlib.pyplot as plt
import numpy as np


class Align(object):

    def __init__(self, app):
        super(Align, self).__init__()
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
        self.laser()

    def laser(self):
        bins = range(0,15)
        fig, self.ax = plt.subplots()
        fig = plt.gcf()

        keys = ["Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg0{}/X/Sensor/Value".format(i) for i in range(1, 10)]
        keys.extend(["Device/SubDeviceList/Platform/LaserSensor/Front/Horizontal/Seg{}/X/Sensor/Value".format(i) for i in range(10, 16)])
        
        while True:
            las_arr = np.absolute(np.array(self.memoryService.getListData(keys)))
            rects = plt.bar(bins, las_arr, align='edge')
            self.autolabel(rects)
            plt.pause(0.01)
            fig.canvas.draw()
            fig.clear()


    def autolabel(self, rects):
        for rect in rects:
            height = rect.get_height()
            self.ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')

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
    ali = Align(app)
    ali.laser()
    app.run()
