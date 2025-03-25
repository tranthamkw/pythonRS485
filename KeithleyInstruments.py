# defining functions for Keitly Instruments
import sys
import time
import re

import rs485Devices

#-----------------------------------------------------------
##		Keitly 485 Ammeter
#-----------------------------------------------------------

def iniK485(rs485address,gpibaddress):
	y=rs485Devices.writeGPIB(rs485address,gpibaddress,'G1R0X',0x0D)
	return y

def readK485(rs485address,gpibaddress):
	returnstring=rs485Devices.listenGPIB(rs485address,gpibaddress,0x0A)

	try:
		value = float(returnstring)
	except:
		value = 0.0

	return value
