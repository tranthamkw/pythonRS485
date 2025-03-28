# defining functions for Sorensen
import sys
import time
import re

import interface.rs485Devices

#-----------------------------------------------------------
##		Sorensen model 120
#-----------------------------------------------------------

def iniK485(rs485address,gpibaddress):
	y=interface.rs485Devices.writeGPIB(rs485address,gpibaddress,'G1R0X',0x0D)
	return y

def readK485(rs485address,gpibaddress):
	returnstring=interface.rs485Devices.listenGPIB(rs485address,gpibaddress,0x0A)

	try:
		value = float(returnstring)
	except:
		value = 0.0

	return value

def initSorensen120(rs485address, gpibaddress):
"""
// default power on is ISET 0.0.  This causes the output to be zero regardlesss of any VSET commend
// all other power defaults should be good
// see page 22 of the Sorensen manual
"""
	y=interface.rs485Devices.writeGPIB(rs485address,gpibaddress,'ISET 0.4',0x0A)

	return y
