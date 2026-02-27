#mcamain.py
import sys
import time
import re
import os
import argparse
import interface.rs485Devices

DELAY=0
DIGIDEVICE=0xDA


# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


parser = argparse.ArgumentParser(
        prog='scanSEE',
        description='Scans KEPCO power supply from start to stop potential',
        epilog="e.g. python scanSEE.py <start v> <end v> <step v>")
parser.add_argument('servo', type=int, help='servo number 0 or 1')
parser.add_argument('pos',type=int,help='position 0 to 8')

args = parser.parse_args()
servo = args.servo
pos=args.pos

z=0
interface.rs485Devices.init()
time.sleep(0.2)

interface.rs485Devices.setRS485ServoPosition(DIGIDEVICE,servo,pos)
time.sleep(0.5)

print(interface.rs485Devices.getRS485ServoPosition(DIGIDEVICE,servo))


print("OK")
interface.rs485Devices.stop()
os._exit(0)
