
#mcamain.py
import sys
import time
import re
import argparse
import os

import interface.rs485Devices


"""
used to check connection to a known device.

ALSO used to program a device's address. To set the device's address, press the button
on the board - leave it pressed and run this code. e.g.

python deviceID.py XX

where XX is the hexidecimal address you want to use. (Make sure no other board is using this
address).  Valid address are 00 through FF

let go the button. The device will remember this address.



"""



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
print("Requesting ID string from RS485 device 0x{:02X}".format(address))

#print("Requesting ID string from RS485 device {}".format(hex(address)))
returnstring = interface.rs485Devices.IDstring(address)

print("ID string: {}".format(returnstring))

print("OK")
interface.rs485Devices.stop()


os._exit(0)
