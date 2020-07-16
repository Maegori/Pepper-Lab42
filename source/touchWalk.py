import naoqi
import qi
import cv2
import functools
import sys

class Stroll(object):
    def __init__(self, app):
        super(Stroll, self).__init__()
        app.start()
        session = app.session

        # Get services
        self.memory = sessions.service("ALMemory")
        self.tts = session.serive("ALTextToSpeech")

        # Connect event callback
        self.touch = self.memory.subscriber("TouchChanged")
        self.id = self.touch.signal.connect(functools.partial(self.onTouched, "TouchChanged"))
        self.language = "Dutch"


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
        app = qi.Application(["HandSqueezer", "--qi-url=" + connection_url])
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    print("Succesfully connected to Pepper @ tcp://" + args.ip + ":" + str(args.port))
    react_to_touch = HandSqueezer(app)
    app.run()