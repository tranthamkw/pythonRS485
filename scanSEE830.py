
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
SRS830 = 0xC5
## these instruments need both the RS485bridge address, and , since GPIB is addressable, we have
## to set the appropriate GPIB address.
K485GPIB=10
K485RS485=0xC3

DELAY=0.1


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

numloops = int((endv-startv)/stepv)+2
if numloops < 1:
	print("num loops too small or startf<endf")
	exit(-1)

filename = fileIO.calculateFilename('SCAN_SEE_') #auto filename

interface.rs485Devices.init()
print("initializing RS830")

SRSinstruments.initSRS830(SRS830)
time.sleep(DELAY)

timeout=interface.rs485Devices.getRS485BridgeTimeout(SRS830)
time.sleep(DELAY)
print("Current timeout {}".format(timeout))

print("Setting timeout to 32")
interface.rs485Devices.setRS485BridgeTimeout(SRS830,32)
time.sleep(DELAY)

timeout=interface.rs485Devices.getRS485BridgeTimeout(SRS830)
time.sleep(DELAY)
print("New timeout {}".format(timeout))



print("initalize K485")
KeithleyInstruments.iniK485(K485RS485,K485GPIB)
time.sleep(DELAY)

k=0
# take the data
print("start data acq")
print('setv,x1,x2,x3,x4,r2,phi2,f')
while k<numloops:
	setv = startv + float(k)*stepv
#	outv=(setv - KEPCO_GAIN_B)/KEPCO_GAIN_M
	print("setv")
	SRSinstruments.setSRS830AD(SRS830,2,setv)
	time.sleep(DELAY)
	print("get AD inputs")
#	the following is supposed to be faster than individual calls 
	x1,x2,x3,x4 = SRSinstruments.getSRS830AuxIn(SRS830)
	"""
	x1=SRSinstruments.getSRS830AD(SRS830,1)
	time.sleep(DELAY)
	x2=SRSinstruments.getSRS830AD(SRS830,2)
	time.sleep(DELAY)
	x3=SRSinstruments.getSRS830AD(SRS830,3)
	time.sleep(DELAY)
	x4=SRSinstruments.getSRS830AD(SRS830,4)
	"""
	time.sleep(DELAY)


	z=KeithleyInstruments.readK485(K485RS485,K485GPIB)
	time.sleep(DELAY)

	r2,phi2,f2 = SRSinstruments.getSRS830Data(SRS830)
	time.sleep(DELAY)

	print("{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{}\t{}\t{}\t{}".format(setv,x1,x2,x3,x4,z,r2,phi2,f2))
	k+=1

# Save it to file


# make a graph?


print("done")

interface.rs485Devices.stop()

os._exit(0)
