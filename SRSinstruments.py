# defining functions for SRS instruments
import sys
import time
import re

import rs485Devices

#	Get Identification string:
#
#	modern SRS instruments will return an id string when presented with '*IDN?'
#	tested: works on : SRS830, SRS335
#	tested: Does not work on : SRS530

def get_ID(address):

	return rs485Devices.writeRS232(address, '*IDN?')

#-----------------------------------------------------------
##		SRS 335 Function generator
#-----------------------------------------------------------
def getSRS335Freq(address):
	cmdData='FREQ?'
	returnstring=rs485Devices.writeRS232(address, cmdData)
	f = float(returnstring)
	return f

def setSRS335Freq(address,f):
	cmdData="FREQ{:.3f}".format(f)
	rs485Devices.writeRS232(address, cmdData)

def getSRS335Ampl(address):
	cmdData='AMPL?'
	returnstring=rs485Devices.writeRS232(address, cmdData)
	# we are expecting a sequence of numbers follwed by VP
	returnstring=re.sub("VP","",returnstring)
	f = float(returnstring)



#-----------------------------------------------------------
##		SRS 830 Digital lockin
#-----------------------------------------------------------

def initSRS830(address):

	"""
	OUTX sets the default interface that the instrument talks with.
		 0 = RS232
		 1 = GPIB
	PHAS0 sets the reference phase shift to zero
	OFLT9 sets time constant to 300mS
	OFSL1
	RMOD2 sets the dynamic reserve to low noise
	DDEF1,1,0 and DDEF2,1,0 sets the displays to R and theta
	RSLP1 sets the reference triger to TTL rising edge
	HARM1 set the detection harmonic to the fundamental of the reference frequency
	"""
	cmdData='OUTX0;OFLT9;PHAS0;RMOD2'
	rs485Devices.writeRS232(address, cmdData)
	cmdData='DDEF1,1,0;DDEF2,1,0;RSLP1;HARM1'
	rs485Devices.writeRS232(address, cmdData)

def getSRS830Data(address):

	cmdData='SNAP?3,4,9'
	returnstring=rs485Devices.writeRS232(address, cmdData)
	if len(returnstring.split(","))==3:
		try:
			r=float(returnstring.split(",")[0])
		except:
			r=0.0
		try:
			phi=float(returnstring.split(",")[1])
		except:
			phi=0.0
		try:
			f =float(returnstring.split(",")[2])
		except:
			f=0.0
	else:
		r=0.0
		phi=0.0
		f=0.0
	return r,phi,f

#-----------------------------------------------------------
##		SRS 530 Analog lockin
#-----------------------------------------------------------

def initSRS530(address):
	"""
	W0 sets the RS232 wait interval to zero. Default is 6, for slower computers c.a. 1980's.geez
	S2 sets the displays to R and theta
	P0 sets the reference phase shift to 0
	D0 sets the dynamic reserve to low noise
	T1,6 sets the time constant to 300ms
	R0 sets the trigger mode to positive
	"""
	cmdData='W0;S2;P0;D0;T1,6;R0'
	rs485Devices.writeRS232(address, cmdData)

def getSRS530Data(address):
	r=0.0
	phi=0.0
	f=0.0
	cmdData='Q1'
	returnstring=rs485Devices.writeRS232(address, cmdData)
	try:
		r = float(returnstring)
	except:
		r=0.0

	time.sleep(0.2)
	cmdData='Q2'
	returnstring=rs485Devices.writeRS232(address, cmdData)
	try:
		phi = float(returnstring)
	except:
		phi=0.0

	time.sleep(0.2)
	cmdData='F'
	returnstring=rs485Devices.writeRS232(address, cmdData)
	try:
		f = float(returnstring)
	except:
		f=0.0

	return r,phi,f
