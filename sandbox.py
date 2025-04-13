#mcamain.py
import sys
import time
import re
import os

import interface.rs485Devices


DIGIDEVICE=0xD0

# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


z=0

interface.rs485Devices.init()
print("getting value")
z=interface.rs485Devices.getRS485DigitalOut(DIGIDEVICE)
print("digital value {}".format(z))
time.sleep(0.2)

print("setting output")
z=interface.rs485Devices.setRS485DigitalIO(DIGIDEVICE,0x0)
time.sleep(0.1)

print("setting value")
z=interface.rs485Devices.setRS485DigitalOut(DIGIDEVICE,0xC)
time.sleep(0.1)

print("getting value")
z=interface.rs485Devices.getRS485DigitalOut(DIGIDEVICE)
print("digital value {}".format(z))
time.sleep(0.5)


print("OK")

interface.rs485Devices.stop()
os._exit(0)
