
from __future__ import print_function


from inputs import get_gamepad, devices, DeviceManager, RawInputDeviceList, GamePad


for devices in devices:
    print(devices)
# def main():
#     """Just print out some event infomation when the gamepad is used."""
#     while 1:
#         events = get_gamepad()
#         for event in events:
#             print(event.ev_type, event.code, event.state)


# if __name__ == "__main__":
#     main()

