import qi
import argparse
import functools
import sys
import time
import pickle


class Swing(object):

    def __init__(self, app):
        super(Swing, self).__init__()
        app.start()
        session = app.session
        # Get services
        self.motion = session.service("ALMotion")
        self.posture = session.service("ALRobotPosture")
    
    def move(self):
        #self.motion.setStiffnesses("Head", 1.0)
        # Example showing a single target angle for one joint
        # Interpolates the head yaw to 1.0 radian in 1.0 second

        animation = dict()
        names = []
        times = []
        keys = []
        isAbsolute = True

        animation = pickle.load("/animations/"+sys.argv[1])

        for k in animation.keys():
            names.append(k)
            times.append(animation[k][0])
            keys.append(animation[k][1])
        
        self.posture.goToPosture("StandInit", 0.5)
        self.motion.angleInterpolation(names, keys, times, isAbsolute)
        time.sleep(1.0)
        
        print("bla")
        

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("Usage: python loadAnimation.py <file.csv in animation folder>")
        sys.exit()

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

