#mcamain.py
import sys
import time
import re
import argparse
import os

import interface.rs485Devices


#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='deviceID',
	description='returns deviceID string from RS485 device at  <address>',
	epilog='e.g. python deviceID.py a3')
parser.add_argument('oldaddress', type=str, help='The address in hex. e.g. A3')
parser.add_argument('newaddress', type=str, help='The address in hex. e.g. A3')

args = parser.parse_args()
oldaddress=int(args.oldaddress,16)
newaddress=int(args.newaddress,16)

interface.rs485Devices.init()

y = interface.rs485Devices.changeAddress(oldaddress,newaddress)

print(y)
print("stop")
interface.rs485Devices.stop()

os._exit(0)
