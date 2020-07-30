import struct
import io
import matplotlib.pyplot as plt
import numpy as np

EVENT_FORMAT = str('llHHi')
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

PATH = "/dev/input/js0"
SIZE = 100

Y = [50495398]
X = [67272614]


with open(PATH, 'rb')as f:
    for i in range(6):
        raw = f.read(EVENT_SIZE)
        struct.unpack(EVENT_FORMAT, raw)

    for i in range(SIZE):
        raw = f.read(EVENT_SIZE)
        data = struct.unpack(EVENT_FORMAT, raw)
        print(data[4])
        if data[4] < 50528251 and data[4] > 50462720:
            Y.append(data[4])
            X.append(X[-1])
        elif data[4] < 67305465 and data[4] > 67239936:
            X.append(data[4])
            Y.append(Y[-1])


X = np.array(X)
Y = np.array(Y)

X = (X - 67272614) / 32678
Y = (Y - 50495398) / 32678
        
plt.scatter(Y, X)
plt.show()
