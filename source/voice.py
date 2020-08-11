
import qi
import argparse
import sys

import time


class Speaker(object):

    def __init__(self, app):
        super(Speaker, self).__init__()
        app.start()
        session = app.session
        # Get services
        self.tts = session.service("ALTextToSpeech")

        self.tts.setLanguage("Dutch")
        self.tts.setParameter("pitchShift", 1.1)
        self.tts.setParameter("speed", 90)

        self.voiceLines()

    def voiceLines(self):
        # 1
        self.tts.say(
            "Dit is allemaal heel interessant, maar ik kan niet wachten \
            totdat de bouw gaat beginnen! \
            \\pau=800\\ \
            Ik wil daarom nu de eerste paal gaan slaan. \
            \\pau=800\\ \
            Gaan jullie mee?"
        )
        time.sleep(2)

        #  2
        self.tts.say(
            "Ja\\emph=200\\, Ik krijg inderdaad mijn eigen robotlab."
        )
        time.sleep(2)

        # 3
        self.tts.say(
            "Ik ga zelf leren op afstand koorts te meten, dat is handig \
            bij bijvoorbeeld een Coronacrisis, \
            \\pau=600\\ \
            en de \\toi=lhp\\n`@Ou\\toi=orth\\ robots zijn natuurlijk aan het trainen \
            voor het wereldkampioenschap voetbal. \
            \\pau=1000\\ \
            Maar bovenop dat hele nieuwe robotlab komt het hele Lab42, \
            vol met innovatie. \
            \\pau=800\\ \
            En dat lab moet wel snel gebouwd worden. \
            \\pau=500\\ \
            Dus kom, laten we de eerste paal gaan slaan!"
        )
        time.sleep(2)

        # 4
        self.tts.say(
            "De eerste paal is geslagen, laat de bouw beginnen! \
            \\pau=800\\ \
            En daar mag op gedronken worden! \
            Ik nodig iedereen uit voor een borrel.\
            \\pau=800\\ \
            Ik drink natuurlijk zelf niet, \
            dus ik ga graag op de foto met wie dat wil."
        )


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
        print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
              "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    print("Succesfully connected to Pepper @ tcp://" +
          args.ip + ":" + str(args.port))
    nav = Speaker(app)
    app.run()


# Device/SubDeviceList/Platform/Front/Sonar/Sensor/Value
# Device/SubDeviceList/Pla`tform/Back/Sonar/Sensor/Value
