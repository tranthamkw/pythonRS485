
#mcamain.py
import sys
import time
import re
import argparse
import os

import rs485Devices


#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='manualRS232',
	description='Send input string to RS485<->232 bridge device at <RS485address>. The string must be meaningful to the RS232 device attached to the bridge.',
	epilog="e.g. python manualRS232.py a2 'this is a test message'")
parser.add_argument('address', type=str, help='The address in hex. e.g. A3')
parser.add_argument('gpib',type=int,help='the gpib address')
parser.add_argument('commandstring', type=str, help='String to send out to RS232 device')

args = parser.parse_args()
address=int(args.address,16)
cmdstr=args.commandstring

rs485Devices.init()

#print("Command string: {}".format(cmdstr))

returnstring=rs485Devices.writeRS232(address, cmdstr)

print(returnstring)

print("OK")
rs485Devices.stop()

os._exit(0)
