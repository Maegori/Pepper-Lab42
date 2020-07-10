
import qi
import argparse
import functools
import sys




class HandSqueezer(object):

    def __init__(self, app):
        super(HandSqueezer, self).__init__()
        app.start()
        session = app.session
        # Get services
        self.memory = session.service("ALMemory")
        self.tts = session.service("ALTextToSpeech")
        # Connect event callback
        self.touch = self.memory.subscriber("TouchChanged")
        self.id = self.touch.signal.connect(functools.partial(self.onTouched, "TouchChanged"))
        self.language = "Dutch"

    def onTouched(self, strVarName, value):
        self.touch.signal.disconnect(self.id)

        parts = []
        for p in value:
            if p[1]:
                parts.append(p[0])
        
        self.say(parts)
        self.id = self.touch.signal.connect(functools.partial(self.onTouched, "TouchChanged"))

    def say(self, bodies):
        if (bodies == []):
            return

        print(bodies)
        sentence = "My " + bodies[0]

        # for b in bodies[1:]:


        #     sentence = sentence + " and my " + b

        # if (len(bodies) > 1):
        #     sentence = sentence + " are"
        # else:
        #     sentence = sentence + " is"
        # sentence = sentence + " touched."
        # self.tts.say(sentence)
    
        
        if "LArm" in bodies or "RArm" in bodies:
            self.tts.say("Are we going on a walk?", self.language)
        else:
            self.tts.say("Stop met mij aan te raken", self.language)

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
