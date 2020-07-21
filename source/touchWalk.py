# # Choregraphe simplified export in Python.
# from naoqi import ALProxy
# names = list()
# times = list()
# keys = list()

# names.append("HeadPitch")
# times.append([0.76, 0.92, 1.04, 1.12, 1.2, 1.32, 1.44, 1.84, 1.92, 2, 2.08, 2.16, 2.4, 2.72, 2.92, 3.04, 3.12, 3.2, 3.32, 3.44, 3.8, 3.88, 3.96, 4.08, 4.2, 5.16])
# keys.append([-0.0628318, -0.120428, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.445059, -0.445059, -0.120428, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.0628318, -0.120428, -0.0383972, -0.120428, -0.0383972, -0.21936])

# names.append("HeadYaw")
# times.append([0.76, 5.16])
# keys.append([0, 0.00306797])

# names.append("HipPitch")
# times.append([0.76, 4.2, 5.16])
# keys.append([-0.769804, -0.769804, -0.0352817])

# names.append("HipRoll")
# times.append([0.76, 4.2, 5.16])
# keys.append([0, 0, 0])

# names.append("KneePitch")
# times.append([0.76, 4.2, 5.16])
# keys.append([0.435392, 0.435392, 0.00153399])

# names.append("LElbowRoll")
# times.append([0.76, 4.2, 5.16])
# keys.append([-1.4312, -1.4312, -0.523087])

# names.append("LElbowYaw")
# times.append([0.76, 4.2, 5.16])
# keys.append([-0.98635, -0.98635, -1.23946])

# names.append("LHand")
# times.append([0.76, 0.92, 1.04, 1.12, 1.2, 1.32, 1.44, 1.84, 1.92, 2, 2.08, 2.16, 2.92, 3.04, 3.12, 3.2, 3.32, 3.44, 3.8, 3.88, 3.96, 4.08, 4.2, 5.16])
# keys.append([0.13181, 0.3, 0.16, 0.29, 0.17, 0.29, 0.17, 0.16, 0.29, 0.17, 0.29, 0.17, 0.3, 0.16, 0.29, 0.17, 0.29, 0.17, 0.16, 0.29, 0.17, 0.29, 0.17, 0.593146])

# names.append("LShoulderPitch")
# times.append([0.76, 2.16, 2.4, 2.72, 2.92, 4.2, 5.16])
# keys.append([0.0260777, 0.0260777, 0.102974, 0.102974, 0.0260777, 0.0260777, 1.55852])

# names.append("LShoulderRoll")
# times.append([0.76, 4.2, 5.16])
# keys.append([0.0628931, 0.0628931, 0.13499])

# names.append("LWristYaw")
# times.append([0.76, 4.2, 5.16])
# keys.append([-0.909704, -0.909704, -0.0138481])

# names.append("RElbowRoll")
# times.append([0.76, 4.2, 5.16])
# keys.append([1.43274, 1.43274, 0.518485])

# names.append("RElbowYaw")
# times.append([0.76, 4.2, 5.16])
# keys.append([0.951068, 0.951068, 1.23486])

# names.append("RHand")
# times.append([0.76, 0.92, 1.04, 1.12, 1.2, 1.32, 1.44, 1.84, 1.92, 2, 2.08, 2.16, 2.92, 3.04, 3.12, 3.2, 3.32, 3.44, 3.8, 3.88, 3.96, 4.08, 4.2, 5.16])
# keys.append([0.13181, 0.3, 0.16, 0.29, 0.17, 0.29, 0.17, 0.16, 0.29, 0.17, 0.29, 0.17, 0.3, 0.16, 0.29, 0.17, 0.29, 0.17, 0.16, 0.29, 0.17, 0.29, 0.17, 0.594903])

# names.append("RShoulderPitch")
# times.append([0.76, 2.16, 2.4, 2.72, 2.92, 4.2, 5.16])
# keys.append([0.0184078, 0.0184078, 0.219911, 0.219911, 0.0184078, 0.0184078, 1.54319])

# names.append("RShoulderRoll")
# times.append([0.76, 4.2, 5.16])
# keys.append([-0.0276118, -0.0276118, -0.127321])

# names.append("RWristYaw")
# times.append([0.76, 4.2, 5.16])
# keys.append([0.906552, 0.906552, 0.0137641])

# try:
#   # uncomment the following line and modify the IP if you use this script outside Choregraphe.
#   motion = ALProxy("ALMotion", "146.50.60.38", 9559)
#   #motion = ALProxy("ALMotion")
#   motion.angleInterpolation(names, keys, times, True)
# except BaseException, err:
#   print err


import qi
import argparse
import sys
import time
import almath


def main(session):
    """
    This example uses the setAngles method and setStiffnesses method
    in order to control joints.
    """
    names = list()
    times = list()
    keys = list()

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
    motion_service  = session.service("ALMotion")
    motion_service.setAngles(names,keys,times)

    time.sleep(3.0)
    motion_service.setStiffnesses("Head", 0.0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="146.50.60.38",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")

    args = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + args.ip + ":" + str(args.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + args.ip + "\" on port " + str(args.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    main(session)