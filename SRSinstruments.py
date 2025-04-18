# defining functions for SRS instruments
import sys
import time
import re

import interface.rs485Devices

""" 		LIST OF FUNCTIONS in this file.
UNLESS otherwise specified, 'address' is the RS485 address of the 485<->232 bridge board

def get_ID(address):
def getSRS335Freq(address):
def setSRS335Freq(address,f):
def getSRS335Ampl(address):

def initSRS830(address):
def getSRS830Data(address):

def initSRS530(address):
def getSRS530Data(address):
def getSRS530AD(address,ch): Back pannel channels 1, 2, 3, or 4: measures Analog in +/- 10V
def setSRS530AD(address,ch,v): Back pannel channels 5 and 6 are Analog outputs +/- 10V.  Channel 5 at power on is a ratio output
and it's initial value unpredicable. Use ch6 first.

"""
#	Get Identification string:
#	SOME SRS machines have this function in common
#	tested: works on : SRS830, SRS335
#	tested: Does not work on : SRS530
def get_ID(address):
	return interface.rs485Devices.writeRS232(address, '*IDN?',0x0D)

#-----------------------------------------------------------
##		SRS 335 Function generator
#-----------------------------------------------------------
""" Returns the currently set frequency of the generator"""
def getSRS335Freq(address):
	cmdData='FREQ?'
	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
	f = float(returnstring)
	return f
""" Sets the frequency of the generator."""
def setSRS335Freq(address,f):
	cmdData="FREQ{:.3f}".format(f)
	interface.rs485Devices.writeRS232(address, cmdData,0x0D)
""" Returns the amplitude of the output"""
def getSRS335Ampl(address):
	cmdData='AMPL?'
	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
	# we are expecting a sequence of numbers follwed by VP
	returnstring=re.sub("VP","",returnstring)
	f = float(returnstring)
"""
Other functions which could be implimented See SRS335 manual for even more:
AECL
The AECL command sets the output to the ECL levels of 1 V peak-to-peak
with a -1.3 V offset. That is, from -1.8V to -0.8V.

AMPL x
The AMPL command sets the output amplitude to x. The value x must
consist of the numerical value and a units indicator. The units may be VP
(Vpp) or VR (Vrms). For example, the command AMPL 1.00VR will set the
output to 1.0 Vrms. Note that the peak AC voltage (Vpp/2) plus the DC offset
voltage must be less than 5 Volts (for 50Ω source). Setting the amplitude to
0 Volts will produce a DC only (no AC function) output controlled by the
OFFS command.

FUNC(?) i
The FUNC command sets the output function type to i. The correspondence
of i and function type is shown in the table below. If the currently selected
frequency is incompatible with the selected function an error will be
generated and the frequency will be set to the maximum allowed for the new
function. The FUNC? query returns the current function.
i Function
0 SINE
1 SQUARE
2 TRIANGLE
3 RAMP
4 NOISE

OFFS(?)x
The OFFS command sets the output's DC offset to x volts. The OFFS?
query returns the current value of the DC offset. The DC offset voltage plus
the peak AC voltage must be less than 5 Volts (into 50Ω).
"""
#-----------------------------------------------------------
##		SRS 830 Digital lockin
#-----------------------------------------------------------
""" Call this first when using the SRS830. It sets common pararmeters
so we know what state the machine is in.  Adjust things like time constant etc
to what you need. See SRS manual"""
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

	0x0D is the terminator required by the SRS830
	"""
	cmdData='OUTX0;OFLT9;PHAS0;RMOD2'
	interface.rs485Devices.writeRS232(address, cmdData,0x0D)
	cmdData='DDEF1,1,0;DDEF2,1,0;RSLP1;HARM1'
	interface.rs485Devices.writeRS232(address, cmdData,0x0D)


def getSRS830Data(address):
	""" See SRS manual.  The SNAP function pulls data at one time, instead of having
	to make repeated calls.  '3,4,9' are the R, theta, and frequency values. Others
	are available
	"""
	cmdData='SNAP?3,4,9'
	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
#	print(returnstring)
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


def getSRS830AuxIn(address):
	""" See SRS manual.  The SNAP function pulls data at one time, instead of having
	to make repeated calls.  '3,4,9' are the R, theta, and frequency values. Others
	are available

	this is supposed to be the FASTER option over individual calls to OAUX
	"""
	cmdData='SNAP?5,6,7,8'
	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
#	print(returnstring)
	if len(returnstring.split(","))==4:
		try:
			r1=float(returnstring.split(",")[0])
		except:
			r1=0.0
		try:
			r2=float(returnstring.split(",")[1])
		except:
			r2=0.0
		try:
			r3=float(returnstring.split(",")[2])
		except:
			r3=0.0
		try:
			r4=float(returnstring.split(",")[2])
		except:
			r4=0.0
	else:
		r1=0.0
		r2=0.0
		r3=0.0
		r4=0.0

	return r1,r2,r3,r4

def getSRS830AD(address,ch):
	"""
	OAUX? i 
	The OAUX? command queries the Aux Input values. The parameter i
	selects an Aux Input (1, 2, 3 or 4) and is required. The Aux Input voltages
	are returned as ASCII strings with units of Volts. The resolution is
	1/3 mV. This command is a query only command.

	"""
	if ch<1:
		ch=1
	if ch>4:
		ch=4
	cmdData="OAUX?{}".format(ch)
	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
	try:
		f = float(returnstring)
	except:
		f=0.0

	return f

def setSRS830AD(address,ch,v):
	"""
	AUXV (?) i {, x}

	The AUXV command sets or queries the Aux Output voltage when the
	output. The parameter i selects an Aux Output (1, 2, 3 or 4) and is
	required. The parameter x is the output voltage (real number of Volts)
	and is limited to -10.500 ≤ x ≤ 10.500. The output voltage will be set to
	the nearest mV.

	"""
	if ch<1:
		ch=1
	if ch>4:
		ch=4
	cmdData="AUXV {},{:.2f}".format(ch,v)
	interface.rs485Devices.writeRS232(address, cmdData,0x0D)




#-----------------------------------------------------------
##		SRS 530 Analog lockin
#-----------------------------------------------------------
"""MUST call this to start using this .  THe most important is 'W0'"""
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
	interface.rs485Devices.writeRS232(address, cmdData,0x0D)

"""this is a wrapper to return the same information as that in the SRS830, above
The SRS530 doesnt have a 'SNAP' so we get the same information piece-meal."""
def getSRS530Data(address):
	r=0.0
	phi=0.0
	f=0.0
	cmdData='Q1'
	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
	try:
		r = float(returnstring)
	except:
		r=0.0

	time.sleep(0.02)
	cmdData='Q2'
	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
	try:
		phi = float(returnstring)
	except:
		phi=0.0

	time.sleep(0.02)
	cmdData='F'
	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
	try:
		f = float(returnstring)
	except:
		f=0.0

	return r,phi,f


def getSRS530AD(address,ch):
	"""X n {,v}
	n designates one of the 6 general purpose analog ports located on the rear panel.
	If n is 1,2,3, or 4,
	the X command will return the voltage on the designated analog input port (X1-X4) in volts.
	"""

	if (ch<1):
		ch=1
	if (ch>6):
		ch=6

	cmdData='X{}'.format(ch)
#debug
#	print("Send command "+cmdData)

	returnstring=interface.rs485Devices.writeRS232(address, cmdData,0x0D)
#debug
#	print("Returnstring "+returnstring)

	try:
		f = float(returnstring)
	except:
		f=0.0

	return f


def setSRS530AD(address,ch,v):
	if ch<5:
		ch=5
	if ch>6:
		ch=6
	cmdData="X{},{:.3f}".format(ch,v)
#debug
#	print("Send command "+ cmdData)
	interface.rs485Devices.writeRS232(address, cmdData,0x0D)

