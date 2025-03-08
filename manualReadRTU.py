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
	prog='manualWriteRTU',
	description='Manually read data from RS485 device <address>, register <register>',
	epilog='text at the bottom')
parser.add_argument('address', type=str, help='The address in hex. e.g. A3')
parser.add_argument('register', type=str, help='The register in hex. e.g. 03')


args = parser.parse_args()
address=int(args.address,16)
register=int(args.register,16)

print("address {}\tregister {}".format(address,register))

usbRS485bridge.start()
time.sleep(0.1)

print("Sending data request...")
y,returndata = usbRS485bridge.read_Modbus_RTU(address,register)

print("return errors? (0=OK) {}".format(y))
time.sleep(0.1)

print("return data {}".format(returndata))


print("stop")
usbRS485bridge.stop()


os._exit(0)
