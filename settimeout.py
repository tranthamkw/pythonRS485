
#scanSEE
import sys
import time
import re
import argparse
import os

import interface.rs485Devices
import SRSinstruments


import fileIO  # There is an 'automatic' file-namer, based on time of day. There MUST be a ~/data directory
# on the raspi


## but we need the RS485<-->RS232 bridge RS485 address.
SRS830 = 0xC7

DELAY=0.1


#								#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#								#

parser = argparse.ArgumentParser(
	prog='settimeout',
	description='sets time out for a RS485-RS232 bridge',
	epilog="e.g. python settimeout.py <time>")
parser.add_argument('address',type=str,help='address')
parser.add_argument('thyme', type=int, help='time')

args = parser.parse_args()
address=int(args.address,16)
t = args.thyme
#do not name variable time.  reserved

interface.rs485Devices.init()

timeout=interface.rs485Devices.getRS485BridgeTimeout(address)
time.sleep(DELAY)
print("Current timeout {}".format(timeout))

print("Setting timeout to {}".format(t))
interface.rs485Devices.setRS485BridgeTimeout(address,t)
time.sleep(DELAY)

timeout=interface.rs485Devices.getRS485BridgeTimeout(address)
time.sleep(DELAY)
print("New timeout {}".format(timeout))




print("done")

interface.rs485Devices.stop()

os._exit(0)
