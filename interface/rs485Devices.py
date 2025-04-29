

#RS485 Devices.py
import sys
import time
import re
import argparse
import os

import interface.usbRS485bridge

# devices register definitions.

BASEREGANLG= 0x0D0D
BASEREGSERVO= 0x0A0A  #also base register for  general purpose digital
# + 16 for read/write to digital IO
# + 8 for read/write to TRIS (this sets if digial IO is in or output)
# +0,+1 servo 0 and servo 1
BASEREG485BRIDGE232= 0x0C0C
# +32 GPIB
BASEREGSTEPMTR= 0x0B0B
BASEAUTOBATT=0X0A2A	#<<<---NEW
BASEREGFN= 0x00F0


battery=[]		#<<<---NEW

"""															#
 interface layer between main (for my digital or analog board),
 or instrument layers(with RS232 or GPIB bridge devices) with usb/RS485 bridge#
															#
"""
#  These are the IO boards to interface with
#	Digital IO board (done)
#	Analog in board
#	Steppermotor board
#	Servo board (done)
#	RS232 bridge (done-ish)
#	GPIB bridge (done)


"""
would it be possible to do object oriented programming?  each card is it's own thing?
the issue is threading and multitasking. only ONE user at a time can access the RS485 bus.
and the user must wait for a reponse from the remote device before releasing control of the
USB resource

Also, the following (init and stop) should only be called once in main

"""

# called at the start of a main
def init():

	for j in range(9):			#<<<---NEW
		battery.append(2**j-1)		#<<<---NEW
	interface.usbRS485bridge.start()

# call this at the end/exit of a main
def stop():
	interface.usbRS485bridge.stop()


"""
 common functions for all of my RS485 cards
"""

# provides the RS485 ID string stored in the device
def IDstring(address):
	y,returndata = interface.usbRS485bridge.read_Modbus_RTU(address,BASEREGFN)
	if (y==0):
		idstring = returndata.decode('utf-8')
	else:
		idstring = "Error occured\n"
	return idstring

def changeAddress(old,new):
	#pic devices need to be reprogrammed for this to work
	#pic's programed before 4/25 assumes
	#outdata[4]=oldAddress
	#outdata[5]=newAddress, and this will not work.
	# For pic's programmed after 4/25
	#consoldating code for the RS485 project puts new address at both [4] and [5]
	"""
	one needs to know that old address for this to work.  if we dont know the address of the 
	board, then hold the 'address-program' button down and use deviceID.py. The board will remember
	the address used as it's own

	This function is inteded to be used in code,AND USED CAREFULLY! Do not change a board's
	address to another address which belongs to another board.
	"""
	y=interface.usbRS485bridge.write_Modbus_RTU(old,0xFF,new)
	return y

"""
				NEW FOR RELAY BATTERY BOX
"""

def setRS485Battery(address,value):  #<<<---NEW
	"""
	ALL OUTPUTS OF RS485 CARD ARE OUTPUTS AND HARDWIRED TO RELAY DRIVERS.
	There are eight DPST relays. When energized, each will insert a 9V battery in series with the relay stack.
	Unenergized is a straight connection.
	The relays are energized in this order for 0,9,18,27,36,45,54,63,72 volts
	OUTVALUE 	Expected battery voltage
	0b00000000 	= 0V
	0b00000001 	= 9V
	0b00000011	= 18V
	0b00000111
	...
	0b00111111
	0b01111111	= 63V
	0b11111111 	= 72V

	the outvalues are set in array 'battery[]', initialize when init() is called.
	"""
	if value<0:
		value=0
	if value>8:
		value=8
	# we can have on of nine, 0 to 8 possible settings. battery[value] determines the outvalue
	y = interface.usbRS485bridge.write_Modbus_RTU(address,BASEAUTOBATT+16,battery[value])
	return y


"""

Digital IO cards.  The following is specific to cards with the
device ID = GPDIGITALIO or DUAL#SERVO(the two high order bits will be ignored)
(if this information is sent to another type of device, it will likely be ignored since the base register
is different for different types of devices.)
"""

def setRS485DigitalOUT(address,value):
	"""
	value & 0F = (in byte order MSB to LSB) RA5 RA4 RC3 RB4
	Setting an "input" to something will not harm, or change the input values.
	It is fine to have the four available bits some mixture of IN and OUT
	"""
	value = value & 0xFF
	y = interface.usbRS485bridge.write_Modbus_RTU(address,BASEREGSERVO+16,value)
	return y

def setRS485DigitalIO(address,value):
	"""
	sets if digital IO's are inputs or outputs. power on default for cards is 'input'
	value & 0F = (in byte order MSB to LSB) TRISA5 TRISA4 TRISC3 TRISB4
	if bit = 1; sets input
	if bit = 0; sets output
	"""
	value = value & 0xFF
	y = interface.usbRS485bridge.write_Modbus_RTU(address,BASEREGSERVO+8,value)
	return y

def getRS485DigitalIN(address):
	"""
	returns status of bits (in byte order MSB to LSB) RA5 RA4 RC3 RB4
	even if one of these bits is an output, we can still read from it

	"""
	y,returndata = interface.usbRS485bridge.read_Modbus_RTU(address,BASEREGSERVO+16)
	value=0
	if (y==0)and len(returndata)==2:
		value=(returndata[0]<<8 | returndata[1])
	else:
		print("error in get data")
	return value
"""
Dual Servo. Device ID = DUAL#SERVO
servo = 0 or 1
position = integer 0 to 8
"""
def setRS485ServoPosition(address, servo, position):
	if (position<0):
		position = 0
	if (position > 10):
		 position = 10
	servo=servo&0x01
	y = interface.usbRS485bridge.write_Modbus_RTU(address,BASEREGSERVO+servo,position)
	return y


def getRS485ServoPosition(address,servo):
	servo=servo&0x01
	y,returndata = interface.usbRS485bridge.read_Modbus_RTU(address,BASEREGSERVO+servo)
	value=0
	if (y==0)and len(returndata)==2:
		value=(returndata[0]<<8 | returndata[1])
	else:
		print("error in get data")

	return value

"""
	RS485 to RS232 bridge card

"""
def writeRS232(rs485address, outstring,terminator):

	y,returndata = interface.usbRS485bridge.write_232_StringRTU(rs485address,BASEREG485BRIDGE232+32,outstring,terminator)
	# y=0 no error.  We generally expect a response when writing to a RS232 device
	# some devices do not send a response, so the operation will(MUST) timeout at the bridge device
	# For devices like this we can set the timeout value for the bridge to something smaller.
	# For devices which we know nothing is returned, the returnstring should not be used.
	if (y==0):
		try:
			returnstring = returndata.decode('utf-8')
		except:
			print("exception decode utf-8. Returndata  {}".format(returndata))
			returnstring="0.0"
	else:
		returnstring="0.0"

	return returnstring

def getRS485BridgeTimeout(Address):

	y,returndata=interface.usbRS485bridge.read_Modbus_RTU(Address,BASEREG485BRIDGE232+2)
#	debug
#	interface.usbRS485bridge.printmybyte(returndata)
	timeout=0
	if (y==0)and len(returndata)==2:
		timeout=(returndata[0]<<8 | returndata[1])
	else:
		print("error in get BridgeTimeout")

	return timeout

def setRS485BridgeTimeout(Address,timeout):
	status = interface.usbRS485bridge.write_Modbus_RTU(Address,BASEREG485BRIDGE232+2,timeout)
	return status


"""
##############################################################
		GPIB  interface card	functions
resetGPIBbridge
writeGPIB	: used when sending a command to a GPIB instrument, where a reponse is not expected
listenGPIB	: used when expecting a response. an instrument specific command is sent with this.

"""
def resetGPIBbridge(rs485address):
	status = interface.usbRS485bridge.write_Modbus_RTU(rs485ddress,BASEREG485BRIDGE232+3,0x00)
	return status

def writeGPIB(rs485address,gpib, outstring,terminator):
	y = interface.usbRS485bridge.write_GPIB_StringRTU(rs485address,BASEREG485BRIDGE232+32,gpib,outstring,terminator)
	return y

def listenGPIB(rs485address,gpib,terminator):
	y,returndata=interface.usbRS485bridge.listen_GPIB_StringRTU(rs485address,BASEREG485BRIDGE232+32,gpib,terminator)
	if (y==0):
		try:
			returnstring = returndata.decode('utf-8')
		except:
			print("exception decode utf-8. Returndata  {}".format(returndata))
			returnstring="0.0"
	else:
		returnstring="0.0"

	return returnstring


