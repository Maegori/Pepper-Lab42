import pickle
import sys

if len(sys.argv) < 2:
    print("Usage: python motionToCSV.py outputName.csv")
    sys.exit()

names = []
keys = []
times = []

### Insert animation from Choregraphe ###

names.append("RElbowRoll")
times.append([3.72, 4.24, 4.72, 5.24, 5.72, 6.24, 10.56, 11.2, 12.08, 12.72, 13.76])
keys.append([0.17334, 0.174873, 0.190213, 0.381962, 1.00783, 1.20724, 1.2225, 1.35949, 1.36364, 1.21294, 0.060054])

names.append("RElbowYaw")
times.append([3.88, 11.16, 11.92, 12.36, 13.44])
keys.append([1.64054, 1.64061, 1.61375, 1.38499, 1.38563])

names.append("RHand")
times.append([3.72, 4.24, 4.72, 5.24, 5.72, 6.24, 6.72, 7.24, 7.72, 8.24, 13.32])
keys.append([0.606327, 0.606327, 0.605448, 0.605448, 0.605448, 0.605448, 0.605448, 0.605448, 0.605448, 0, 0.02])

names.append("RShoulderPitch")
times.append([3.72, 9.84, 10.24, 10.72, 11.16, 11.4, 11.6, 11.92, 12.16, 12.32, 12.6, 12.84, 13.36, 13.56, 13.8])
keys.append([1.36064, 1.35974, 1.25633, 0.972545, 0.512793, 0.0214758, -0.279314, -0.743725, -1.03697, -1.1987, -1.19037, -1.04464, -0.216035, 0.365633, 0.670917])

names.append("RShoulderRoll")
times.append([3.72, 4.24, 9.84, 12.4, 13.76])
keys.append([-0.147262, -0.226893, -0.226893, -0.41388, -0.146608])

names.append("RWristYaw")
times.append([3.72, 4.24, 4.72, 5.24, 5.72, 6.24, 6.72, 8.36, 8.72, 9.24, 9.72, 11.92, 12.16, 12.44, 13.28])
keys.append([0.0137641, 0.00302602, -0.00310993, 0.185572, 0.688724, 1.32687, 1.51862, 1.51844, 1.19648, 0.148756, -0.0049172, 0.0260564, 0.0925888, 0.170469, 0.241218])


#########################################

motion = dict()

for i, n in enumerate(names):
    motion[n] = [times[i], keys[i]]

print(keys)

with open("../source/animations/"+sys.argv[1]+".pickle", 'wb') as f:
    pickle.dump(motion, f)



