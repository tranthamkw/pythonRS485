#mcamain.py
import sys
import time
import re
import os

import interface.rs485Devices

DELAY=0
DIGIDEVICE=0xD0

# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


z=0

interface.rs485Devices.init()
print("getting value")
z=interface.rs485Devices.getRS485DigitalIN(DIGIDEVICE)
print("digital value {}".format(z))
#time.sleep(DELAY)



print("setting output")
z=interface.rs485Devices.setRS485DigitalIO(DIGIDEVICE,0x0)
#time.sleep(DELAY)

for j in range(16):
	print("setting value {}".format(j))
	z=interface.rs485Devices.setRS485DigitalOUT(DIGIDEVICE,j)
#	time.sleep(DELAY)
	z=interface.rs485Devices.getRS485DigitalIN(DIGIDEVICE)
	print("return value {}".format(z))
#	time.sleep(DELAY)


print("OK")

interface.rs485Devices.stop()
os._exit(0)
