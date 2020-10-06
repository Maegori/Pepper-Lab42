#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

"""Example: Use showImage Method"""

import qi
import argparse
import sys
import time


class Image(object):

    def __init__(self, app):
        super(Image, self).__init__()
        app.start()
        self.session = app.session
        self.image()

    def image(self):

       
        tabletService = self.session.service("ALTabletService")
        tabletService.setBackgroundColor("#0000000")
        tabletService.pauseGif()

        # Display a local image located in img folder in the root of the web server
        # The ip of the robot from the tablet is 198.18.0.1
        print(tabletService.showImage("https://ivi.fnwi.uva.nl/sne/wp-content/uploads/2017/01/UVA-LOGO.png"))

        time.sleep(5)

        # Hide the web view
        tabletService.hideImage()
        tabletService.resumeGif()
        print("here")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="146.50.60.38",
                        help="Robot IP address. On robot or Local Naoqi: use '146.50.60.38'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    parser.add_argument("--animation", type=str,
                        help="Name of the animation to play")

    args = parser.parse_args()
    try:
        # Initialize qi framework.
        connection_url = "tcp://" + args.ip + ":" + str(args.port)
        app = qi.Application(["Image", "--qi-url=" + connection_url])
    except RuntimeError:
        print("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) + ".\n"
              "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)

    print("Succesfully connected to Pepper @ tcp://" +
          args.ip + ":" + str(args.port))
    img = Image(app)
    app.run()