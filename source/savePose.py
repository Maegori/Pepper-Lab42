import qi
import argparse
import functools
import sys


"""
Python script to save the current pose that Pepper is in. Poses can be 
manipulated by hand through the animation mode in Choregraphe. The 
poses themself are saved locally on pepper.

https://sebastianwallkoetter.wordpress.com/2019/04/05/the-hidden-potential-of-nao-and-pepper-custom-robot-postures-in-naoqi-v2-4/
"""

class Pose(object):

    def __init__(self, app):
        super(Pose, self).__init__()
        app.start()
        session = app.session
        # Get services
        self.motion = session.service("ALMotion")
        self.posture = session.service("ALRobotPosture")

        self.record()

    def record(self):
        pos_id = 4242
        pos_name = "handOpen"
        pos_file_name = "custom_pose.pose"

        #save current posture
        self.posture._saveCurrentPostureWithName(pos_id, pos_name)

        # add neighbouring postures
        stand_pos_id = self.posture._getIdFromName("Stand")
        self.posture._addNeighbourToPosture(stand_pos_id, pos_id, 1)
        self.posture._addNeighbourToPosture(pos_id, stand_pos_id, 1)

        # save posture
        self.posture._savePostureLibrary(pos_file_name)

        # load posture
        self.posture._loadPostureLibraryFromName(pos_file_name)
        self.posture._generateCartesianMap()

        # play new posture
        self.posture.goToPosture("Stand", 0.5)
        self.posture.goToPosture(pos_name, 0.5)


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
    p = Pose(app)
    app.run()