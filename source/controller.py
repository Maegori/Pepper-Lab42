import io
import struct
import math

EVENT_FORMAT = str('llHHi')
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)

PATH = "/dev/input/js0"

X = [50495398]
Y = [67272614]

with open(PATH, 'rb')as f:
    for i in range(6):
        struct.unpack(EVENT_FORMAT, f.read(EVENT_SIZE))

    while True:
        data = struct.unpack(EVENT_FORMAT, f.read(EVENT_SIZE))
        if data[4] < 50528251 and data[4] > 50462720:
            X.append(data[4])
            Y.append(Y[-1])

            x = round(float(X[-1] - 50495398) / 32678, 1)
            y = round(float(Y[-1] - 67272614) / 32678, 1)

            x = 1 + x if x < 0 else x - 1
            y = -(y + 1) if y < 0 else 1 - y

            print(round(x, 2), round(y, 2))
        elif data[4] < 67305465 and data[4] > 67239936:
            Y.append(data[4])
            X.append(X[-1])

            x = round(float(X[-1] - 50495398) / 32678, 1)
            y = round(float(Y[-1] - 67272614) / 32678, 1)

            x = 1 + x if x < 0 else x - 1
            y = -(y + 1) if y < 0 else 1 - y

            print(round(x, 2), round(y, 2))