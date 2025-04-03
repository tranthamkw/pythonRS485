
#scanSEE
import sys
import time
import re
import argparse
import os

import interface.rs485Devices
import SRSinstruments

import KeithleyInstruments

import fileIO  # There is an 'automatic' file-namer, based on time of day. There MUST be a ~/data directory
# on the raspi


## these instruments are connected by RS232. No address is required for the instrument itself
## but we need the RS485<-->RS232 bridge RS485 address.
SRS530 = 0xCA
## these instruments need both the RS485bridge address, and , since GPIB is addressable, we have
## to set the appropriate GPIB address.
K485GPIB=10
K485RS485=0xC2

#constants for conversion
KEPCO_GAIN_M=10.2 #this is slope of your calibration graph. Change this to actual
KEPCO_GAIN_B=1.5 #this is the y-int of your calibration graph. Change this to actual
# i am assuming that kepcoOut= M * vin + B
# so	voutX6 = (desiredKepcoOut - B)/M

SR570_1SCALE=1e-6
SR570_2SCALE=1e-9
VDIVIDER=0.12 #voltage divider determined by R1&R2. change to actual

instrumentDiagram="""

	+-------+
	|	|
	|	+------<X1-------<[SR570]<----- Electrode 1
	|SRS	|
	|530	+------<X2-------<[SR570]<----- Electrode 2
	|	|
	|	+------<X3-------------+-----/\R1/\-----+
	|	|	GND---/\R2/\---+		|
	|	|					|
	|	+------>X6>------>[Kepco x10]>----------------> Electrode 3
	|	|
	|	|
	+-------+
	  |   |
	  R   Theta

		<-----[Keithly485]<-----------------<Electrode4

"""

#								#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#								#

parser = argparse.ArgumentParser(
	prog='scanSEE',
	description='Scans KEPCO power supply from start to stop potential. Records data from lockin SRS530 lockin.',
	epilog="e.g. python scanSEE.py <start v> <end v> <step v>")
parser.add_argument('startv', type=float, help='start volts')
parser.add_argument('endv', type=float, help='end volts')
parser.add_argument('stepv',type = float, help='step volts')

args = parser.parse_args()
startv = args.startv
endv = args.endv
stepv = args.stepv

#TODO put in check to ensure startv and endv are in the 0 - 120V range

numloops = int((endv-startv)/stepv)+2
if numloops < 1:
	print("num loops too small or startf<endf")
	exit(-1)


filename = fileIO.calculateFilename('SCAN_SEE_') #auto filename

interface.rs485Devices.init()
print("initializing RS530")
SRSinstruments.initSRS530(SRS530)
time.sleep(0.1)

KeithleyInstruments.iniK485(K485RS485,K485GPIB)

# lists to hold data
# somebody needs to teach me numpy
actualv=[]
current1=[]
current2=[]
current3=[]
lockinR=[]
lockinPhi=[]

k=0
# take the data
print("start data acq")
print('setv,outv,tempv,tempI1,tempI2,z,r2,phi2,f')
while k<numloops:
	setv = startv + float(k)*stepv
	outv=(setv - KEPCO_GAIN_B)/KEPCO_GAIN_M
	SRSinstruments.setSRS530AD(SRS530,6,outv)
	time.sleep(0.05)
	# read in actual from X3
	tempv=(SRSinstruments.getSRS530AD(SRS530,3))/VDIVIDER
	actualv.append(tempv)
	time.sleep(0.05)
	#read current amplifier 1
	tempI1=(SRSinstruments.getSRS530AD(SRS530,1))*SR570_1SCALE
	current1.append(tempI1)
	time.sleep(0.05)
	#read current amplifier 2
	tempI2=(SRSinstruments.getSRS530AD(SRS530,2))*SR570_2SCALE
	current2.append(tempI2)
	time.sleep(0.05)
	#read keithly 485
	z=KeithleyInstruments.readK485(K485RS485,K485GPIB)
	time.sleep(0.1)
	current3.append(z)
	#read r and phi
	r2,phi2,f2 = SRSinstruments.getSRS530Data(SRS530)
	lockinR.append(r2)
	lockinPhi.append(phi2)

	print("{}\t{:.3f}\t{:.3f}\t{:.3f}\t{}\t{}\t{}\t{}\t{}".format(setv,outv,tempv,tempI1,tempI2,z,r2,phi2,f2))
	k+=1

# Save it to file


# make a graph?


print("done")

interface.rs485Devices.stop()

os._exit(0)
