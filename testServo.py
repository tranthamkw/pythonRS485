#mcamain.py
import sys
import time
import re
import os
import argparse
import interface.rs485Devices

DELAY=0


# this is a sand pit to test various things before wrapping into a dedicated main script#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#


parser = argparse.ArgumentParser(
        prog='testServo',
        description='Sets servo position',
        epilog="e.g. python testServo.py <servo> <pos>")
parser.add_argument('address',type=str,help='the address in hex')
parser.add_argument('servo', type=int, help='servo number 0 or 1')
parser.add_argument('pos',type=int,help='position 0 to 8')

args = parser.parse_args()
servo = args.servo
pos=args.pos
address = int(args.address,16)

z=0
interface.rs485Devices.init()
time.sleep(0.2)

interface.rs485Devices.setRS485ServoPosition(address,servo,pos)
time.sleep(0.5)

print(interface.rs485Devices.getRS485ServoPosition(address,servo))


print("OK")
interface.rs485Devices.stop()
os._exit(0)
