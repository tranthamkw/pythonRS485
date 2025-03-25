

#RS485 Devices.py
import sys
import time
import re
import argparse
import os

import usbRS485bridge

# devices register definitions.

BASEREGANLG= 0x0D0D
BASEREGSERVO= 0x0A0A
BASEREG485BRIDGE232= 0x0C0C
BASEREGSTEPMTR= 0x0B0B
BASEREGFN= 0x00F0

#															#
# interface layer between main, or instrument layers, with usb/RS485 bridge#
#															#

#  These are the IO boards to interface with
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
	y,returndata = usbRS485bridge.read_Modbus_RTU(address,BASEREGFN)
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


def writeRS232(rs485address, outstring,terminator):

	y,returndata = usbRS485bridge.write_232_StringRTU(rs485address,BASEREG485BRIDGE232+32,outstring,terminator)
	# y=0 no error.  We generally expect a response when writing to a RS232 device
	# some devices do not send a response, so the operation will timeout at the bridge device
	# for devices like this we can set the timeout value for the bridge to something smaller.
	# for devices which we know nothing is returned, the returnstring should not be used.
	if (y==0):
		try:
			returnstring = returndata.decode('utf-8')
		except:
			print("exception decode utf-8. Returndata  {}".format(returndata))
			returnstring="0.0"
	else:
		returnstring="0.0"

	return returnstring

"""
##############################################################

		GPIB	functions

resetGPIBbridge
writeGPIB	: used when sending a command to a GPIB instrument, where a reponse is not expected
listenGPIB	: used when expecting a response. an instrument specific command is sent with this.

"""
def resetGPIBbridge(rs485address):
	status = usbRS485bridge.write_Modbus_RTU(rs485ddress,BASEREG485BRIDGE232+3,0x00)
	return status

def writeGPIB(rs485address,gpib, outstring,terminator):
	y = usbRS485bridge.write_GPIB_StringRTU(rs485address,BASEREG485BRIDGE232+32,gpib,outstring,terminator)
	return y

def listenGPIB(rs485address,gpib,terminator):
	y,returndata=usbRS485bridge.listen_GPIB_StringRTU(rs485address,BASEREG485BRIDGE232+32,gpib,terminator)
	if (y==0):
		try:
			returnstring = returndata.decode('utf-8')
		except:
			print("exception decode utf-8. Returndata  {}".format(returndata))
			returnstring="0.0"
	else:
		returnstring="0.0"

	return returnstring


