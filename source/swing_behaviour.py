
import qi
import argparse
import functools
import sys


class Swing(object):

    def __init__(self, app):
        super(Swing, self).__init__()
        app.start()
        session = app.session
        # Get services
        self.motion = session.service("ALMotion")
        self.posture = session.service("ALRobotPosture")

    def move(self):
        self.posture.goToPosture("StandInit", 0.5)

        names = []
        times = []
        keys = []

        names.append("HeadPitch", )
        times.append([0.76, 0.92, 1.04, 1.12, 1.2, 1.32, 1.44, 1.84, 1.92, 2, 2.08, 2.16, 2.4, 2.72, 2.92, 3.04, 3.12, 3.2, 3.32, 3.44, 3.8, 3.88, 3.96, 4.08, 4.2, 5.16])
        keys.append([-0.0628318, -0.120428, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.445059, -0.445059, -0.120428, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.21936])

        isAbsolute = True
        self.motion.angleInterpolation(names, keys, times, isAbsolute)        
        print("bla")
        

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
    swing_motion = Swing(app)
    swing_motion.move()
    app.run()
