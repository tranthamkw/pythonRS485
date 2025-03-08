
#mcamain.py
import sys
import time
#import serial
#import port
import re
import argparse
import os
#import threading
#from datetime import datetime

import usbRS485bridge

#import globalVars


#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='deviceID',
	description='returns deviceID string from RS485 device at  <address>',
	epilog='text at the bottom')
parser.add_argument('address', type=str, help='The address in hex. e.g. A3')

idstring=""
args = parser.parse_args()
address=int(args.address,16)

usbRS485bridge.start()
time.sleep(0.1)

print("Requesting ID string from RS485 device {}".format(hex(address)))

y,returndata = usbRS485bridge.read_Modbus_RTU(address,0xF0)

#print("return errors? (0=OK) {}".format(y))
#time.sleep(0.1)
if (y==0):
	idstring = returndata.decode('utf-8')
	print("ID string: {}".format(idstring))

print("stop")
usbRS485bridge.stop()


os._exit(0)
