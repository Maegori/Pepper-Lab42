
import qi
import argparse
import functools
import sys
import time



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

        names = []
        times = []
        keys = []

        names.append("HeadPitch")
        times.append([0.76, 0.92, 1.04, 1.12, 1.2, 1.32, 1.44, 1.84, 1.92, 2, 2.08, 2.16, 2.4, 2.72, 2.92, 3.04, 3.12, 3.2, 3.32, 3.44, 3.8, 3.88, 3.96, 4.08, 4.2, 5.16])
        keys.append([-0.0628318, -0.120428, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.445059, -0.445059, -0.120428, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.21936])

        names.append("HeadYaw")
        times.append([0.76, 5.16])
        keys.append([0, 0.00306797])

        names.append("HipPitch")
        times.append([0.76, 4.2, 5.16])
        keys.append([-0.769804, -0.769804, -0.0352817])

        names.append("HipRoll")
        times.append([0.76, 4.2, 5.16])
        keys.append([0, 0, 0])

        names.append("KneePitch")
        times.append([0.76, 4.2, 5.16])
        keys.append([0.435392, 0.435392, 0.00153399])

        names.append("LElbowRoll")
        times.append([0.76, 4.2, 5.16])
        keys.append([-1.4312, -1.4312, -0.523087])

        names.append("LElbowYaw")
        times.append([0.76, 4.2, 5.16])
        keys.append([-0.98635, -0.98635, -1.23946])

        names.append("LHand")
        times.append([0.76, 0.92, 1.04, 1.12, 1.2, 1.32, 1.44, 1.84, 1.92, 2, 2.08, 2.16, 2.92, 3.04, 3.12, 3.2, 3.32, 3.44, 3.8, 3.88, 3.96, 4.08, 4.2, 5.16])
        keys.append([0.13181, 0.3, 0.16, 0.29, 0.17, 0.29, 0.17, 0.16, 0.29, 0.17, 0.29, 0.17, 0.3, 0.16, 0.29, 0.17, 0.29, 0.17, 0.16, 0.29, 0.17, 0.29, 0.17, 0.593146])

        names.append("LShoulderPitch")
        times.append([0.76, 2.16, 2.4, 2.72, 2.92, 4.2, 5.16])
        keys.append([0.0260777, 0.0260777, 0.102974, 0.102974, 0.0260777, 0.0260777, 1.55852])

        names.append("LShoulderRoll")
        times.append([0.76, 4.2, 5.16])
        keys.append([0.0628931, 0.0628931, 0.13499])

        names.append("LWristYaw")
        times.append([0.76, 4.2, 5.16])
        keys.append([-0.909704, -0.909704, -0.0138481])

        names.append("RElbowRoll")
        times.append([0.76, 4.2, 5.16])
        keys.append([1.43274, 1.43274, 0.518485])

        names.append("RElbowYaw")
        times.append([0.76, 4.2, 5.16])
        keys.append([0.951068, 0.951068, 1.23486])

        names.append("RHand")
        times.append([0.76, 0.92, 1.04, 1.12, 1.2, 1.32, 1.44, 1.84, 1.92, 2, 2.08, 2.16, 2.92, 3.04, 3.12, 3.2, 3.32, 3.44, 3.8, 3.88, 3.96, 4.08, 4.2, 5.16])
        keys.append([0.13181, 0.3, 0.16, 0.29, 0.17, 0.29, 0.17, 0.16, 0.29, 0.17, 0.29, 0.17, 0.3, 0.16, 0.29, 0.17, 0.29, 0.17, 0.16, 0.29, 0.17, 0.29, 0.17, 0.594903])

        names.append("RShoulderPitch")
        times.append([0.76, 2.16, 2.4, 2.72, 2.92, 4.2, 5.16])
        keys.append([0.0184078, 0.0184078, 0.219911, 0.219911, 0.0184078, 0.0184078, 1.54319])

        names.append("RShoulderRoll")
        times.append([0.76, 4.2, 5.16])
        keys.append([-0.0276118, -0.0276118, -0.127321])

        names.append("RWristYaw")
        times.append([0.76, 4.2, 5.16])
        keys.append([0.906552, 0.906552, 0.0137641])
        isAbsolute = True
        
        self.posture.goToPosture("StandInit", 0.5)

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

