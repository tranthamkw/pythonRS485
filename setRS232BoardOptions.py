
#scanSEE
import sys
import time
import re
import argparse
import os

import interface.rs485Devices
import SRSinstruments


DELAY=0.3


#								#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#								#

parser = argparse.ArgumentParser(
	prog='setRS232BoardOptions',
	description='sets time out for a RS485-RS232 bridge',
	epilog="e.g. python settimeout.py <time> <1,0>")
parser.add_argument('address',type=str,help='address')
parser.add_argument('thyme', type=int, help='time-out in ms')
parser.add_argument('debugprint', type=int, help='set debug print')

args = parser.parse_args()
address=int(args.address,16)
t = args.thyme
dbp=args.debugprint

"""

NEVER name a variable 'time'. this is reserved. an


"""
interface.rs485Devices.init()


timeout=interface.rs485Devices.getRS485BridgeTimeout(address)

time.sleep(DELAY)

print("Current timeout {} ms".format(timeout))

print("Setting timeout to {} ms".format(t))
interface.rs485Devices.setRS485BridgeTimeout(address,t)
time.sleep(DELAY)

timeout=interface.rs485Devices.getRS485BridgeTimeout(address)
time.sleep(DELAY)
print("New timeout {}".format(timeout))

debugprint=interface.rs485Devices.getRS485BridgeDBP(address)
time.sleep(DELAY)
print("Current debugprint {}".format(debugprint))

print("Setting debugprint to {}".format(dbp))
interface.rs485Devices.setRS485BridgeDBP(address,dbp)
time.sleep(DELAY)

dbp=interface.rs485Devices.getRS485BridgeDBP(address)
time.sleep(DELAY)
print("New debugprint {}".format(dbp))

print("done")

interface.rs485Devices.stop()

os._exit(0)
