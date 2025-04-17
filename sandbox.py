#mcamain.py
import sys
import time
import re
import os

import interface.rs485Devices

DELAY=0
DIGIDEVICE=0xD0
SERVODEVICE=0xD3

# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


z=0

interface.rs485Devices.init()
print("getting value")
z=interface.rs485Devices.getRS485ServoPosition(SERVODEVICE,1)
print("digital value {}".format(z))
#time.sleep(DELAY)

for j in range(9):
	print("setting value {}".format(j))
	z=interface.rs485Devices.setRS485ServoPosition(SERVODEVICE,1,j)
#	time.sleep(DELAY)
	z=interface.rs485Devices.getRS485ServoPosition(SERVODEVICE,1)
	print("return value {}".format(z))
#	time.sleep(DELAY)

z=interface.rs485Devices.setRS485ServoPosition(SERVODEVICE,1,0)

print("OK")

interface.rs485Devices.stop()
os._exit(0)
