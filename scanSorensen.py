
#mcamain.py
import sys
import time
import re
import argparse
import os

import interface.rs485Devices
import SRSinstruments
import fileIO
import KeithleyInstruments
import Sorensen
## these instruments are connected by RS232. No address is required for the instrument itself
## but we need the RS485<-->RS232 bridge RS485 address.
SRS830 = 0xC5
SRS530 = 0xCA
SRS335 = 0xC0

## these instruments need both the RS485bridge address, and , since GPIB is addressable, we have
## to set the appropriate GPIB address.
K485GPIB=10
K485RS485=0xC3

SORENSENRS485=0xC9
SORENSENGPIB=0x0C
#															#
# ++++++++++++++++++++	START MAIN +++++++++++++++++++++++#
#															#

parser = argparse.ArgumentParser(
	prog='scanSorensen',
	description='Scans Sorencen power supply from start to stop potential. Records data from Sorensen,Keithly ammeter, SRS830 lockin, and SRS530 lockin.',
	epilog="e.g. python scanSRS.py <start v> <end v> <step v>")
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



filename = fileIO.calculateFilename('SCAN_Sorensen_')

r=0.0
phi=0.0
f=0.0

interface.rs485Devices.init()
print("initializing RS830")
SRSinstruments.initSRS830(SRS830)
time.sleep(0.1)
returnstring=SRSinstruments.get_ID(SRS830)
print("Found "+returnstring)

print("initializing RS530")
SRSinstruments.initSRS530(SRS530)
time.sleep(0.1)


KeithleyInstruments.iniK485(K485RS485,K485GPIB)
Sorensen.initSorensen120(SORENSENRS485, SORENSENGPIB)


with open(filename,mode='w') as f:
	f.write("setv,actualv,sorensenI,KeiethlyI,r1,phi1,f1,r2,phi2,f2\n")
	k=0
	while k<numloops:
		setv = startv + float(k)*stepv
		Sorensen.setSorensen120Volts(SORENSENRS485, SORENSENGPIB, setv)
		time.sleep(1)
		actv=Sorensen.getSorensen120Volts(SORENSENRS485, SORENSENGPIB)
		time.sleep(0.1)
		acti=Sorensen.getSorensen120Amps(SORENSENRS485, SORENSENGPIB)
		time.sleep(0.5)
		z=KeithleyInstruments.readK485(K485RS485,K485GPIB)
		time.sleep(0.1)
		r1,phi1,f1 = SRSinstruments.getSRS830Data(SRS830)
		time.sleep(0.2)
		r2,phi2,f2 = SRSinstruments.getSRS530Data(SRS530)
		print("{}\t{}\t{}\t{}\t\t{}\t{}\t{}\t{}\t{}".format(setv,actv,acti,z,r1,phi1,f1,r2,phi2,f2))
		f.write("{},{},{},{},{},{},{},{},{},{}\n".format(setv,actv,acti,z,r1,phi1,f1,r2,phi2,f2))
		time.sleep(0.2)
		k+=1



Sorensen.setSorensen120Volts(SORENSENRS485, SORENSENGPIB, 0.0)

print("OK")

interface.rs485Devices.stop()

os._exit(0)
