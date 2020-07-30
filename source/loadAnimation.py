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

        names.append("HipPitch")
        times.append([0.3, 1.16667, 2.43333, 2.8])
        keys.append([[-0.177553, [3, -0.111111, 0], [3, 0.288889, 0]], [-0.342986, [3, -0.288889, 0.0296132], [3, 0.422222, -0.0432808]], [-0.396235, [3, -0.422222, 0], [3, 0.122222, 0]], [-0.147349, [3, -0.122222, 0], [3, 0, 0]]])

        names.append("RElbowRoll")
        times.append([0.3, 1.3, 1.96667, 2.43333])
        keys.append([[0.0184078, [3, -0.111111, 0], [3, 0.333333, 0]], [1.37369, [3, -0.333333, -0.0326131], [3, 0.222222, 0.021742]], [1.39544, [3, -0.222222, 0], [3, 0.155556, 0]], [0.401903, [3, -0.155556, 0], [3, 0, 0]]])

        names.append("RElbowYaw")
        times.append([0.3, 2.43333])
        keys.append([[1.73186, [3, -0.111111, 0], [3, 0.711111, 0]], [1.68278, [3, -0.711111, 0], [3, 0, 0]]])

        names.append("RHand")
        times.append([0.3, 2.43333])
        keys.append([[0.535149, [3, -0.111111, 0], [3, 0.711111, 0]], [0.507909, [3, -0.711111, 0], [3, 0, 0]]])

        names.append("RShoulderPitch")
        times.append([0.3, 1.2, 2.1, 2.56667, 2.76667])
        keys.append([[1.46342, [3, -0.111111, 0], [3, 0.3, 0]], [0.128854, [3, -0.3, 0.417272], [3, 0.3, -0.417272]], [-1.04022, [3, -0.3, 0], [3, 0.155556, 0]], [0.477687, [3, -0.155556, -0.631924], [3, 0.0666667, 0.270824]], [1.66803, [3, -0.0666667, 0], [3, 0, 0]]])

        names.append("RShoulderRoll")
        times.append([0.3, 2.43333])
        keys.append([[-0.0905049, [3, -0.111111, 0], [3, 0.711111, 0]], [-0.18738, [3, -0.711111, 0], [3, 0, 0]]])

        names.append("RWristYaw")
        times.append([0.3, 2.43333])
        keys.append([[-0.219404, [3, -0.111111, 0], [3, 0.711111, 0]], [-0.383542, [3, -0.711111, 0], [3, 0, 0]]])
        
        self.posture.goToPosture("StandInit", 1)
        print(len(names), len(keys), len(times))
        self.motion.angleInterpolation(names, keys, times, isAbsolute)
        time.sleep(1.0)
        
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

