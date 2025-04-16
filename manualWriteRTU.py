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

import interface.usbRS485bridge

#import globalVars

"""

manually write to RS485 device registers using MODBUS-RTU encoding

This program is a diagnostic tool and not typically used for routine stuff

YOU MUST KNOW WHAT YOU ARE DOING


"""
#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='manualWriteRTU',
	description='Manually send data to RS485 device <address>, register <register>/nYOU MUST KNOW WHAT YOU,RE DOING!',
	epilog='e.g. python manualWriteRTU.py a3 06 123')
parser.add_argument('address', type=str, help='The address in hex. e.g. A3')
parser.add_argument('register', type=str, help='The register in hex. e.g. 03')
parser.add_argument('data', type=int, help='data to send')


args = parser.parse_args()
address=int(args.address,16)
register=int(args.register,16)
mydata=args.data

print("address {}\tregister {}\tdata {}".format(address,register,mydata))

interface.usbRS485bridge.start()
time.sleep(0.1)

print("Sending...")
y=interface.usbRS485bridge.write_Modbus_RTU(address,register,mydata)

print("return errors? (0=OK) {}".format(y))
time.sleep(0.1)

print("stop")
interface.usbRS485bridge.stop()


os._exit(0)
