
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

import interface.rs485Devices

#import globalVars


#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='deviceID',
	description='returns deviceID string from RS485 device at  <address>',
	epilog='e.g. python deviceID.py a3')
parser.add_argument('address', type=str, help='The address in hex. e.g. A3')

idstring=""
args = parser.parse_args()
address=int(args.address,16)

interface.rs485Devices.init()

print("Requesting ID string from RS485 device {}".format(hex(address)))
returnstring = interface.rs485Devices.IDstring(address)

print("ID string: {}".format(returnstring))

print("OK")
interface.rs485Devices.stop()


os._exit(0)
