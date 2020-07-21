import pickle
import sys

motion = dict()
names = []
times = []
keys = []

with open(sys.argv[1], 'rb') as f:
    motion = pickle.load(f)

for k in motion.keys():
    print(k, motion[k][0], motion[k][1])
    print()

