#mcamain.py
import sys
import time
import re
import argparse
import os

import usbRS485bridge

#import globalVars

"""

manually read from a RS485 device registers using MODBUS-RTU encoding

This program is a diagnostic tool and not typically used for routine stuff

YOU MUST KNOW WHAT YOU ARE DOING  


"""

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
