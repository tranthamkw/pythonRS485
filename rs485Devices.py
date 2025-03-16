

#RS485 Devices.py
import sys
import time
import re
import argparse
import os

import usbRS485bridge



#															#
# interface layer between main, or instrument layers, with usb/RS485 bridge#
#															#

#  These are the functions to interface with
#	digital IO board
#	Analog in board
#	steppermotor board
#	etc
#	RS232 bridge
#	GPIB bridge


# called at the start of a main 
def init():
	usbRS485bridge.start()

# call this at the end/exit of a main
def stop():
	usbRS485bridge.stop()

# provides the RS485 ID string stored in the device
def IDstring(address):
	y,returndata = usbRS485bridge.read_Modbus_RTU(address,usbRS485bridge.BASEREGFN)
	if (y==0):
		idstring = returndata.decode('utf-8')
	else:
		idstring = "Error occured\n"
	return idstring

def changeAddress(old,new):
	#pic devices need to be reprogrammed for this to work
	#present pic programminmg assumes
	#outdata[4]=oldAddress
	#outdata[5]=newAddress
	#but consoldating puts new address at both 4 and 5
	y=usbRS485bridge.write_Modbus_RTU(old,0xF0,new)
	return y


def writeRS232(rs485address, outstring):

	y,returndata = usbRS485bridge.write_Bridge_StringRTU(rs485address, outstring)
	if (y==0):
		try:
			returnstring = returndata.decode('utf-8')
		except:
			print("exception decode utf-8. Returndata  {}".format(returndata))
			returnstring="0.0"
	else:
		returnstring="0.0"

	return returnstring
