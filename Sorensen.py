# defining functions for Sorensen
import sys
import time
import re

import interface.rs485Devices

#-----------------------------------------------------------
##		Sorensen model 120
#-----------------------------------------------------------

def getSorensen120Amps(rs485address, gpibaddress):

	y=interface.rs485Devices.writeGPIB(rs485address,gpibaddress,'IOUT?',0x0A)

	if y==0:
		returnstring=interface.rs485Devices.listenGPIB(rs485address,gpibaddress,0x0A)
#		print(returnstring)
		"""
		 format of return data
		 IOUT 12.9<CR><LF>
		  strips the first four characters
		"""
		if len(returnstring)>4:
			returnstring=re.sub("IOUT","",returnstring)
		else:
			print("getSorensenAmps: return unexpected length")
			value=0.0
		try:
			value = float(returnstring)
		except:
			print("Sorensent returnedn"+returnstring+" expecting a float")
			value = 0.0
	else:
		print("error connecting to Sorenson RS485ch: {} and GPIB {}".format(rs485address,gpibaddress))
		value = 0.0

	return value



def getSorensen120Volts(rs485address, gpibaddress):

	y=interface.rs485Devices.writeGPIB(rs485address,gpibaddress,'VOUT?',0x0A)

	if y==0:
		returnstring=interface.rs485Devices.listenGPIB(rs485address,gpibaddress,0x0A)

		"""
		 format of return data
		 VOUT 12.9<CR><LF>
		  strips the first four characters
		"""
		if len(returnstring)>4:
			returnstring=re.sub("VOUT","",returnstring)
		else:
			print("getSorensenVolts: return unexpected length")
			value=0.0
		try:
			value = float(returnstring)
		except:
			print("Sorensent returnedn"+returnstring+" expecting a float")
			value = 0.0
	else:
		print("error connecting to Sorenson RS485ch: {} and GPIB {}".format(rs485address,gpibaddress))
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


def setSorensen120Volts(rs485address, gpibaddress,myvolts):
        cmdData="VSET {:.1f}".format(myvolts)
        interface.rs485Devices.writeGPIB(rs485address,gpibaddress, cmdData,0x0A)
