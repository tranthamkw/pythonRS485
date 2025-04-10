
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
	prog='manualRS232',
	description='Send input string to GPIB bridge device at <RS485address>.\
 The string must be meaningful to the GPIB device attached to the bridge.\
The program waits 0.5s, then instructs the device to talk. The reponse is echoed',
	epilog="e.g. python manualRSGPIB.py a2 gpib 'this is a test message'")
parser.add_argument('address', type=str, help='The address in hex. e.g. A3')
parser.add_argument('gpib',type=int,help='the gpib address')
parser.add_argument('commandstring', type=str, help='String to send out to RS232 device')

args = parser.parse_args()
address=int(args.address,16)
cmdstr=args.commandstring
gpib = args.gpib
interface.rs485Devices.init()

#print("Command string: {}".format(cmdstr))

interface.rs485Devices.writeGPIB(address,gpib,cmdstr,0x0D)

time.sleep(0.5)

returnstring=interface.rs485Devices.listenGPIB(address,gpib,0x0A)

print(returnstring)
print("Done")
interface.rs485Devices.stop()
os._exit(0)
