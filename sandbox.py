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
        prog='scanSEE',
        description='Scans KEPCO power supply from start to stop potential',
        epilog="e.g. python scanSEE.py <start v> <end v> <step v>")
parser.add_argument('startv', type=int, help='start volts')

args = parser.parse_args()
x = args.startv


z=0

interface.rs485Devices.init()

for k in range(5):
	for j in range(9):
		z=interface.rs485Devices.setRS485Battery(DIGIDEVICE,j)
		sys.stdout.write("{} ".format(j))
		sys.stdout.flush()
		time.sleep(0.1)
	sys.stdout.write("\n")

	for j in range(8,-1,-1):
		z=interface.rs485Devices.setRS485Battery(DIGIDEVICE,j)
		sys.stdout.write("{} ".format(j))
		sys.stdout.flush()
		time.sleep(0.1)
	sys.stdout.write("\n")

time.sleep(0.1)

z=interface.rs485Devices.setRS485Battery(DIGIDEVICE,0)

print("OK")

interface.rs485Devices.stop()
os._exit(0)
