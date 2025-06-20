#mcamain.py
import sys
import time
import re
import os
import argparse
import interface.rs485Devices

DELAY=0
DIGIDEVICE=0xC4
SERVODEVICE=0xD3


# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


parser = argparse.ArgumentParser(
        prog='battboxtest',
        description='sets battbox to one of nine possible outputs ',
        epilog="e.g. python battboxtest.py <idx>")
parser.add_argument('idx', type=int, help='index. possible values 0 through 9')
args = parser.parse_args()
x = args.idx


interface.rs485Devices.init()

z=interface.rs485Devices.setRS485Battery(DIGIDEVICE,x)
"""
for k in range(2):
	for j in range(9):
		z=interface.rs485Devices.setRS485Battery(DIGIDEVICE,j)
		sys.stdout.write("{} ".format(j))
		sys.stdout.flush()
		time.sleep(0.5)
	sys.stdout.write("\n")

	for j in range(8,-1,-1):
		z=interface.rs485Devices.setRS485Battery(DIGIDEVICE,j)
		sys.stdout.write("{} ".format(j))
		sys.stdout.flush()
		time.sleep(0.5)
	sys.stdout.write("\n")

time.sleep(0.1)

z=interface.rs485Devices.setRS485Battery(DIGIDEVICE,0)
"""
print("OK")

interface.rs485Devices.stop()
os._exit(0)
